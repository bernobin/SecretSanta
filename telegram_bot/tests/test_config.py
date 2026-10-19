
import unittest

from secret_santa_bot.config import load_settings

TEST_ENVIRONMENT = {
    "TELEGRAM_BOT_TOKEN": "test-token",
    "SECRET_SANTA_API_BASE_URL": "http://localhost:8000",
}


class LoadSettingsTests(unittest.TestCase):
    def test_loads_telegram_token(self) -> None:
        environ = TEST_ENVIRONMENT.copy()

        settings = load_settings(environ)
        self.assertEqual(settings.telegram_bot_token, "test-token")

    def test_rejects_empty_token(self) -> None:
        environ = TEST_ENVIRONMENT.copy()
        environ["TELEGRAM_BOT_TOKEN"] = ""

        with self.assertRaisesRegex(ValueError, "must not be empty"):
            load_settings(environ)

    def test_rejects_missing_token(self) -> None:
        environ = TEST_ENVIRONMENT.copy()
        del environ["TELEGRAM_BOT_TOKEN"]

        with self.assertRaises(KeyError):
            load_settings(environ)

    def test_rejects_whitespace_only_token(self) -> None:
        environ = TEST_ENVIRONMENT.copy()
        environ["TELEGRAM_BOT_TOKEN"] = "   "

        with self.assertRaisesRegex(ValueError, "must not be empty"):
            load_settings(environ)

    def test_loads_api_base_url(self) -> None:
        environ = TEST_ENVIRONMENT.copy()
        settings = load_settings(environ)

        self.assertEqual(settings.api_base_url, "http://localhost:8000")

    def test_rejects_empty_api_base_url(self) -> None:
        environ = TEST_ENVIRONMENT.copy()
        environ["SECRET_SANTA_API_BASE_URL"] = ""

        with self.assertRaisesRegex(ValueError, "must not be empty"):
            load_settings(environ)

    def test_rejects_missing_api_base_url(self) -> None:
        environ = TEST_ENVIRONMENT.copy()
        del environ["SECRET_SANTA_API_BASE_URL"]

        with self.assertRaises(KeyError):
            load_settings(environ)

    def test_rejects_whitespace_only_api_base_url(self) -> None:
        environ = TEST_ENVIRONMENT.copy()
        environ["SECRET_SANTA_API_BASE_URL"] = "   "

        with self.assertRaisesRegex(ValueError, "must not be empty"):
            load_settings(environ)


if __name__ == "__main__":
    unittest.main()
