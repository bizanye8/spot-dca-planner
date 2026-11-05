# Spot DCA Planner

![Type](https://img.shields.io/badge/strategy-spot%20only-3fb950?style=flat-square)
![Leverage](https://img.shields.io/badge/leverage-none-3fb950?style=flat-square)
![Liquidation risk](https://img.shields.io/badge/liquidation%20risk-zero-2f81f7?style=flat-square)

**Plan a staged spot entry before the market moves — tranches, a running average cost, and rebound scenarios. No leverage, no liquidation line, no improvisation mid-drawdown.**

Built by a trader who learned the difference between paper profits and settled profits the expensive way: leveraged positions are closed by the path, spot positions are closed by the plan.

## What it does

- Splits a capital budget into **staged tranches** along a geometric price ladder (first price → last price)
- Weighting modes: **equal**, **increasing** (heavier tranches lower — the classic dip-accumulation shape), **decreasing**
- Tracks **cumulative size and running average cost** after every tranche
- Prints a **scenario table**: position value, P/L and return at the ladder bottom, your average, the ladder top, 2× your average, and your rebound target

## Run it

**In the browser:** open [`index.html`](index.html) — everything runs locally, defaults are preloaded with a worked example.

**On the command line:**

```bash
python3 planner.py --asset SOL --capital 20000 --from 150 --to 60 \
    --stages 6 --weighting increasing --target 250
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
