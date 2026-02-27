import tempfile
import unittest
from pathlib import Path

from macro_forecast.telegram_webhook import process_update


class TelegramWebhookTest(unittest.TestCase):
    def test_process_subscribe_command(self):
        with tempfile.TemporaryDirectory() as td:
            db = Path(td) / "subs.json"
            update = {
                "update_id": 1,
                "message": {
                    "chat": {"id": 12345},
                    "text": "/subscribe daily",
                },
            }
            action = process_update(db, update)
            self.assertEqual(action.chat_id, "12345")
            self.assertIsNotNone(action.reply_text)
            self.assertIn("구독", action.reply_text)


if __name__ == "__main__":
    unittest.main()
