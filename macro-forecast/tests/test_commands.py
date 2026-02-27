import tempfile
import unittest
from pathlib import Path

from macro_forecast.commands import handle_command


class CommandTest(unittest.TestCase):
    def test_subscribe_status_unsubscribe(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "outputs").mkdir(parents=True, exist_ok=True)
            (root / "outputs" / "daily.md").write_text("DAILY REPORT", encoding="utf-8")
            db = root / "data" / "subscribers.json"
            db.parent.mkdir(parents=True, exist_ok=True)

            r1 = handle_command(db, "telegram", "u1", "/subscribe weekly")
            self.assertTrue(r1.ok)
            r2 = handle_command(db, "telegram", "u1", "/status")
            self.assertIn("weekly", r2.reply)
            r_help = handle_command(db, "telegram", "u1", "/help")
            self.assertIn("/today", r_help.reply)
            r_today = handle_command(db, "telegram", "u1", "/today")
            self.assertIn("DAILY REPORT", r_today.reply)
            r3 = handle_command(db, "telegram", "u1", "/unsubscribe")
            self.assertTrue(r3.ok)


if __name__ == "__main__":
    unittest.main()
