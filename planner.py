#!/usr/bin/env python3
"""Spot DCA Planner — staged spot entries, average-cost math, rebound scenarios.

Spot only. A position built this way has no liquidation price; the plan is
decided in advance so a drawdown is executed, not improvised.

Usage:
    python3 planner.py --capital 20000 --from 150 --to 60 --stages 6 \
        --weighting increasing --target 250 --asset SOL
"""

import argparse


def build_plan(capital, p_start, p_end, stages, weighting):
    if stages == 1:
        prices = [p_start]
    else:
        ratio = p_end / p_start
        prices = [p_start * ratio ** (i / (stages - 1)) for i in range(stages)]
    if weighting == "equal":
        weights = [1.0] * stages
    elif weighting == "increasing":
        weights = [float(i + 1) for i in range(stages)]
    else:  # decreasing
        weights = [float(stages - i) for i in range(stages)]
    total_w = sum(weights)
    tranches, cum_coins, cum_cost = [], 0.0, 0.0
    for price, w in zip(prices, weights):
        usd = capital * w / total_w
        coins = usd / price
        cum_coins += coins
        cum_cost += usd
        tranches.append((price, usd, coins, cum_coins, cum_cost / cum_coins))
    return tranches, cum_coins, cum_cost / cum_coins


def main():
    ap = argparse.ArgumentParser(description="Staged spot-buying planner (no leverage).")
    ap.add_argument("--asset", default="SOL")
    ap.add_argument("--capital", type=float, default=20000, help="total USDT to deploy")
    ap.add_argument("--from", dest="p_start", type=float, default=150, help="first tranche price")
    ap.add_argument("--to", dest="p_end", type=float, default=60, help="last tranche price")
    ap.add_argument("--stages", type=int, default=6)
    ap.add_argument("--weighting", choices=["equal", "increasing", "decreasing"], default="increasing")
    ap.add_argument("--target", type=float, default=250, help="rebound target price")
    a = ap.parse_args()

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


if __name__ == "__main__":
    main()
