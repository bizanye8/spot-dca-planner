#!/usr/bin/env python3
"""Spot DCA Planner — staged spot entries, average-cost math, rebound scenarios,
and a backtest of the same plan against real daily price history.

Spot only. A position built this way has no liquidation price; the plan is
decided in advance so a drawdown is executed, not improvised.

Plan mode:
    python3 planner.py --capital 20000 --from 150 --to 60 --stages 6 \
        --weighting increasing --target 250 --asset SOL

Backtest mode (walks the baked SOL daily series in data/sol-daily.json):
    python3 planner.py --backtest --start 2026-01-01 --capital 20000 \
        --stages 6 --depth 0.5 --weighting increasing
"""

import argparse
import json
import os


def ladder(p_start, p_end, stages):
    if stages == 1:
        return [p_start]
    ratio = p_end / p_start
    return [p_start * ratio ** (i / (stages - 1)) for i in range(stages)]


def weights_for(stages, weighting):
    if weighting == "equal":
        return [1.0] * stages
    if weighting == "increasing":
        return [float(i + 1) for i in range(stages)]
    return [float(stages - i) for i in range(stages)]  # decreasing


def build_plan(capital, p_start, p_end, stages, weighting):
    prices = ladder(p_start, p_end, stages)
    weights = weights_for(stages, weighting)
    total_w = sum(weights)
    tranches, cum_coins, cum_cost = [], 0.0, 0.0
    for price, w in zip(prices, weights):
        usd = capital * w / total_w
        coins = usd / price
        cum_coins += coins
        cum_cost += usd
        tranches.append((price, usd, coins, cum_coins, cum_cost / cum_coins))
    return tranches, cum_coins, cum_cost / cum_coins


def simulate(series, capital, stages, depth, weighting):
    """Walk daily closes; a tranche fills the first day close <= its trigger.

    Returns (fills, total_coins, spent, equity_curve). Unfilled tranches
    remain as cash in the equity curve.
    """
    start_price = series[0]["close"]
    triggers = ladder(start_price, start_price * (1 - depth), stages)
    weights = weights_for(stages, weighting)
    total_w = sum(weights)
    fills = [None] * stages
    coins = spent = 0.0
    equity = []
    for day in series:
        for i, trigger in enumerate(triggers):
            if fills[i] is None and day["close"] <= trigger:
                usd = capital * weights[i] / total_w
                fills[i] = {"date": day["date"], "price": day["close"],
                            "usd": usd, "coins": usd / day["close"]}
                coins += fills[i]["coins"]
                spent += usd
        equity.append((capital - spent) + coins * day["close"])
    return fills, coins, spent, equity


def print_plan(a):
    tranches, total_coins, avg = build_plan(a.capital, a.p_start, a.p_end, a.stages, a.weighting)
    print(f"\n{a.asset} staged spot plan — {a.capital:,.0f} USDT, {a.stages} tranches ({a.weighting})")
    print(f"{'#':>3} {'price':>12} {'USDT in':>12} {a.asset:>12} {'cum. coins':>12} {'avg cost':>12}")
    for i, (p, usd, coins, cum, run_avg) in enumerate(tranches, 1):
        print(f"{i:>3} {p:>12,.4f} {usd:>12,.2f} {coins:>12,.4f} {cum:>12,.4f} {run_avg:>12,.4f}")
    print(f"\nTotal: {total_coins:,.4f} {a.asset} at average cost {avg:,.4f} USDT")
    levels = sorted({a.p_end, avg, a.p_start, avg * 2, a.target})
    print(f"\n{'price':>12} {'value':>14} {'P/L':>14} {'return':>9}")
    for p in levels:
        value = total_coins * p
        pl = value - a.capital
        tag = " (target)" if p == a.target else " (your avg)" if p == avg else ""
        print(f"{p:>12,.4f} {value:>14,.2f} {pl:>+14,.2f} {pl / a.capital * 100:>+8.1f}%{tag}")
    print("\nSpot cannot be liquidated. The plan's job is to remove improvisation from the drawdown.")


def print_backtest(a):
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "sol-daily.json")
    with open(path) as f:
        series_all = json.load(f)["points"]
    series = [d for d in series_all if d["date"] >= a.start]
    if not series:
        print("No data on/after", a.start)
        return
    fills, coins, spent, equity = simulate(series, a.capital, a.stages, a.depth, a.weighting)
    start_price, end_price = series[0]["close"], series[-1]["close"]
    avg = spent / coins if coins else 0.0
    final_eq = equity[-1]
    bench = a.capital / start_price * end_price
    print(f"\nBacktest — SOL from {series[0]['date']} (${start_price:,.2f}) to {series[-1]['date']} (${end_price:,.2f})")
    print(f"Plan: {a.capital:,.0f} USDT, {a.stages} stages, depth -{a.depth * 100:.0f}%, {a.weighting}")
    for i, f in enumerate(fills, 1):
        if f:
            print(f"  #{i} filled {f['date']} @ {f['price']:,.2f} — {f['usd']:,.2f} USDT -> {f['coins']:,.4f} SOL")
        else:
            print(f"  #{i} never triggered — cash held")
    print(f"\nFilled {sum(1 for f in fills if f)}/{a.stages} tranches · {coins:,.4f} SOL · avg cost {avg:,.2f}")
    print(f"Plan final equity:  {final_eq:,.2f} USDT ({(final_eq / a.capital - 1) * 100:+.1f}%)")
    print(f"All-in at start:    {bench:,.2f} USDT ({(bench / a.capital - 1) * 100:+.1f}%)")
    print("Fills use daily closes; fees excluded; unfilled tranches stay as cash.")


def main():
    ap = argparse.ArgumentParser(description="Staged spot-buying planner (no leverage).")
    ap.add_argument("--asset", default="SOL")
    ap.add_argument("--capital", type=float, default=20000)
    ap.add_argument("--from", dest="p_start", type=float, default=150)
    ap.add_argument("--to", dest="p_end", type=float, default=60)
    ap.add_argument("--stages", type=int, default=6)
    ap.add_argument("--weighting", choices=["equal", "increasing", "decreasing"], default="increasing")
    ap.add_argument("--target", type=float, default=250)
    ap.add_argument("--backtest", action="store_true", help="run the backtest instead of the plan")
    ap.add_argument("--start", default="2026-01-01", help="backtest start date (YYYY-MM-DD)")
    ap.add_argument("--depth", type=float, default=0.5, help="backtest ladder depth, e.g. 0.5 = -50%%")
    a = ap.parse_args()
    if a.backtest:
        print_backtest(a)
    else:
        print_plan(a)


if __name__ == "__main__":
    main()
