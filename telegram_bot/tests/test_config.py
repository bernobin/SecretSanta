
import unittest

from secret_santa_bot.config import load_settings


class LoadSettingsTests(unittest.TestCase):
    def test_loads_telegram_token(self) -> None:
        settings = load_settings(
            {"TELEGRAM_BOT_TOKEN": "test-token"}
        )

        self.assertEqual(settings.telegram_bot_token, "test-token")

    def test_rejects_empty_token(self) -> None:
        with self.assertRaisesRegex(
            ValueError,
            "must not be empty",
        ):
            load_settings({"TELEGRAM_BOT_TOKEN": ""})

    def test_rejects_missing_token(self) -> None:
        with self.assertRaises(KeyError):
            load_settings({})

    def test_rejects_whitespace_only_token(self) -> None:
        with self.assertRaisesRegex(
            ValueError,
            "must not be empty",
        ):
            load_settings({"TELEGRAM_BOT_TOKEN": "   "})


if __name__ == "__main__":
    unittest.main()
