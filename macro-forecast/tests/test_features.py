import unittest

from macro_forecast.features import derive_features_from_levels


class FeaturesTest(unittest.TestCase):
    def test_pct_change(self):
        cur = {"us_cpi_yoy": 3.0, "fed_funds_rate": 5.25}
        prev = {"us_cpi_yoy": 2.5, "fed_funds_rate": 5.0}
        f = derive_features_from_levels(cur, prev)
        self.assertGreater(f["us_cpi_yoy_change"], 0)
        self.assertGreater(f["fed_rate_change"], 0)


if __name__ == "__main__":
    unittest.main()
