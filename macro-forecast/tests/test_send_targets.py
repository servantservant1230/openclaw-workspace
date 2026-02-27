import tempfile
import unittest
from pathlib import Path

from macro_forecast.subscriptions import SubscriptionStore


class SendTargetTest(unittest.TestCase):
    def test_filter_telegram_subs(self):
        with tempfile.TemporaryDirectory() as td:
            db = Path(td) / "subs.json"
            s = SubscriptionStore(db)
            s.subscribe("telegram", "100", "daily")
            s.subscribe("webchat", "current", "daily")
            arr = [x for x in s.for_cadence("daily") if x.channel == "telegram"]
            self.assertEqual(len(arr), 1)
            self.assertEqual(arr[0].target, "100")


if __name__ == "__main__":
    unittest.main()
