import tempfile
import unittest
from pathlib import Path

from macro_forecast.subscriptions import SubscriptionStore


class SubscriptionTest(unittest.TestCase):
    def test_subscribe_and_filter(self):
        with tempfile.TemporaryDirectory() as td:
            store = SubscriptionStore(Path(td) / "subs.json")
            store.subscribe("webchat", "user:me", "daily")
            store.subscribe("webchat", "user:me2", "all")
            daily = store.for_cadence("daily")
            self.assertEqual(len(daily), 2)
            monthly = store.for_cadence("monthly")
            self.assertEqual(len(monthly), 1)


if __name__ == "__main__":
    unittest.main()
