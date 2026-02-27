import unittest

from macro_forecast.backtest import evaluate_rows


class BacktestTest(unittest.TestCase):
    def test_evaluate_rows(self):
        rows = [
            {
                "date": "2026-01-01",
                "fed_rate_change": "0.0",
                "us10y_change": "0.0",
                "dxy_change": "0.0",
                "brent_change": "0.0",
                "usdkrw_change": "0.0",
                "ai_capex_momentum": "0.0",
                "memory_cycle": "0.0",
                "export_momentum": "0.0",
                "real_nasdaq_dir": "FLAT",
            }
        ]
        out = evaluate_rows(rows, ["nasdaq"])
        self.assertEqual(out["nasdaq"].samples, 1)
        self.assertGreaterEqual(out["nasdaq"].accuracy, 0.0)


if __name__ == "__main__":
    unittest.main()
