import tempfile
import unittest
from pathlib import Path

from macro_forecast.commands import handle_command


class CommandTest(unittest.TestCase):
    def test_subscribe_status_unsubscribe(self):
        with tempfile.TemporaryDirectory() as td:
            db = Path(td) / "subscribers.json"
            r1 = handle_command(db, "telegram", "u1", "/subscribe weekly")
            self.assertTrue(r1.ok)
            r2 = handle_command(db, "telegram", "u1", "/status")
            self.assertIn("weekly", r2.reply)
            r3 = handle_command(db, "telegram", "u1", "/unsubscribe")
            self.assertTrue(r3.ok)


if __name__ == "__main__":
    unittest.main()
