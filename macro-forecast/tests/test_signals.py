import unittest

from macro_forecast.signals import build_signal_map


class SignalTest(unittest.TestCase):
    def test_basic_keys_exist(self):
        sig = build_signal_map({
            "fed_rate_change": 0.0,
            "us10y_change": 0.1,
            "dxy_change": 0.0,
            "brent_change": 0.0,
            "usdkrw_change": 0.1,
            "ai_capex_momentum": 0.5,
            "memory_cycle": 0.4,
            "export_momentum": 0.3,
        })
        for key in ["nasdaq", "qqq", "kospi", "samsung_electronics", "sk_hynix", "naver"]:
            self.assertIn(key, sig)


if __name__ == "__main__":
    unittest.main()
