# Spot DCA Planner

![Type](https://img.shields.io/badge/strategy-spot%20only-3fb950?style=flat-square)
![Leverage](https://img.shields.io/badge/leverage-none-3fb950?style=flat-square)
![Liquidation risk](https://img.shields.io/badge/liquidation%20risk-zero-2f81f7?style=flat-square)
[![Tests](https://github.com/bizanye8/spot-dca-planner/actions/workflows/tests.yml/badge.svg)](https://github.com/bizanye8/spot-dca-planner/actions/workflows/tests.yml)
![Demo](https://img.shields.io/badge/demo-live-2f81f7?style=flat-square)

**Plan a staged spot entry before the market moves — then backtest the same plan against 1,000 days of real price history. No leverage, no liquidation line, no improvisation mid-drawdown.**

### ▶ Live demo: [bizanye8.github.io/spot-dca-planner](https://bizanye8.github.io/spot-dca-planner/)

Built by a trader who learned the difference between paper profits and settled profits the expensive way: leveraged positions are closed by the path; spot positions are closed by the plan.

## What it does

**Plan mode**
- Splits a capital budget into **staged tranches** along a geometric price ladder
- Weighting modes: **equal**, **increasing** (heavier lower — the dip-accumulation shape), **decreasing**
- Tracks **cumulative size and running average cost** per tranche
- **Scenario table**: value / P&L / return at the ladder bottom, your average, the ladder top, 2× average, and your rebound target
- **Export the plan as CSV**

**Backtest mode** (the v2 headline)
- Walks your ladder through **real SOL daily closes, 2024-02 → 2026-11** (Binance public data, baked into [`data/sol-daily.json`](data/sol-daily.json) — the demo works fully offline)
- Start near the cycle top, mid-range, or in the crash; set stages, ladder depth (−30% / −50% / −70%) and weighting
- Reports fills day by day, final equity, and the honest benchmark: **what going all-in on day one would have done**
- Equity-vs-price chart with fill points marked

## What the backtest actually shows (real runs, $20,000, 6 stages, −50% depth, increasing)

| Start | Market did | Staged plan | All-in at start |
|---|---|---|---|
| 2026-01-01 ($126.90) | fell to $62, recovered to $91.70 | **+20.8%** (avg cost $75.89) | −27.7% |
| 2025-01-19 ($252.42, near top) | long slide to $91.70 | **−37.4%** | −63.7% |

Read both rows. Staging is not magic — starting at the top still loses. What it does is mechanical: it converts panic territory into pre-committed purchases, keeps dry powder for the actual lows, and drags the average cost down to where a recovery — not a new all-time high — puts you back in profit.

## Run it

**Browser:** the [live demo](https://bizanye8.github.io/spot-dca-planner/), or open [`index.html`](index.html) locally (backtest data loads from the repo file).

**Command line:**

```bash
# plan mode
python3 planner.py --asset SOL --capital 20000 --from 150 --to 60 \
    --stages 6 --weighting increasing --target 250

# backtest mode
python3 planner.py --backtest --start 2026-01-01 --capital 20000 \
    --stages 6 --depth 0.5 --weighting increasing

# tests
python3 -m unittest discover -s tests
```

## The idea in one paragraph

Elastic assets (SOL-type beta) reward staged entries: you cannot know the bottom, so you buy a *range* instead of a point. Each tranche is sized in advance, the average cost falls as price falls, and because the position is spot, no wick can close it. Exits are staged the same way. What this tool removes is not risk — it removes *decisions made under stress*.

## Worked reference points (spot, $20,000)

| Entry | Exit | Multiple | Profit |
|---|---|---|---|
| ETH $1,000 | $3,000 | 3.0× | +$40,000 |
| SOL $10 | $250 | 25× | +$480,000 |
| SUI $0.30 | $4.00 | 13.3× | +$246,667 |

Paper numbers are easy; holding through −50% drawdowns on the way is the actual strategy. The plan is how.

---

*Not financial advice. A planning tool by [BizAnyE](https://github.com/bizanye8) — Web3 operations & community, 3+ years trading spot and perpetuals.*
