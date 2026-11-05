import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from planner import build_plan, ladder, simulate, weights_for  # noqa: E402


class TestLadder(unittest.TestCase):
    def test_endpoints(self):
        prices = ladder(150, 60, 6)
        self.assertAlmostEqual(prices[0], 150)
        self.assertAlmostEqual(prices[-1], 60)

    def test_monotonic_down(self):
        prices = ladder(200, 50, 8)
        self.assertTrue(all(a > b for a, b in zip(prices, prices[1:])))

    def test_single_stage(self):
        self.assertEqual(ladder(100, 40, 1), [100])


class TestPlan(unittest.TestCase):
    def test_capital_fully_allocated(self):
        tranches, _, _ = build_plan(20000, 150, 60, 6, "increasing")
        self.assertAlmostEqual(sum(t[1] for t in tranches), 20000)

    def test_avg_cost_inside_ladder(self):
        _, _, avg = build_plan(20000, 150, 60, 6, "equal")
        self.assertTrue(60 <= avg <= 150)

    def test_weights_sum(self):
        self.assertEqual(sum(weights_for(6, "increasing")), 21)


class TestBacktest(unittest.TestCase):
    def setUp(self):
        # price falls 100 -> 45, then recovers to 90
        self.series = ([{"date": f"2026-01-{d:02d}", "close": 100 - 5 * d} for d in range(1, 12)]
                       + [{"date": "2026-02-01", "close": 90.0}])

    def test_tranches_fill_on_the_way_down(self):
        fills, coins, spent, equity = simulate(self.series, 1000, 3, 0.5, "equal")
        self.assertTrue(all(f is not None for f in fills))
        self.assertGreater(coins, 0)
        self.assertAlmostEqual(spent, 1000)

    def test_equity_ends_at_cash_plus_position(self):
        fills, coins, spent, equity = simulate(self.series, 1000, 3, 0.5, "equal")
        self.assertAlmostEqual(equity[-1], coins * 90.0)

    def test_unfilled_when_price_never_dips(self):
        rising = [{"date": f"2026-03-{d:02d}", "close": 100 + d} for d in range(1, 8)]
        fills, coins, spent, _ = simulate(rising, 1000, 3, 0.5, "equal")
        self.assertIsNotNone(fills[0])            # first tranche fills at the open
        self.assertTrue(any(f is None for f in fills))  # deeper tranches never trigger
        self.assertLess(spent, 1000)              # unfilled capital stays as cash


if __name__ == "__main__":
    unittest.main()
