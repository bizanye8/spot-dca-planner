# Changelog

## v2.0 — 2026-11-05

- **Backtest mode**: walk any staged plan through 1,000 days of real SOL daily closes (2024-02 → 2026-11, Binance public data baked into `data/sol-daily.json`)
- Start-date presets (cycle top / mid-range / crash), ladder depth −30% / −50% / −70%, all weighting modes
- Equity-vs-price chart with fill points; day-by-day fill table; all-in benchmark comparison
- **CSV export** of the plan table
- CLI backtest in `planner.py` (`--backtest --start … --depth …`)
- Unit tests: 9 cases covering ladder math, allocation, and the simulator (`tests/`)

## v1.0 — 2026-11-05

- Staged plan builder: geometric ladder, three weighting modes, running average cost
- Scenario table (value / P&L / return at key prices)
- Browser app (`index.html`) and CLI (`planner.py`)
