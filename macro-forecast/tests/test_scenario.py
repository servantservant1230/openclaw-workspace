import unittest

from macro_forecast.scenario import build_asset_scenarios


class ScenarioTest(unittest.TestCase):
    def test_scenario_keys(self):
        out = build_asset_scenarios({"ai_capex_momentum": 0.1})
        self.assertIn("us_equity", out)
        self.assertIn("kr_equity", out)


if __name__ == "__main__":
    unittest.main()
