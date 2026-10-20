import unittest

from secret_santa_bot.api_client import create_api_client
from secret_santa_bot.config import Settings
from secret_santa_bot.generated_client.secret_santa_api_client import Client


class CreateApiClientTests(unittest.TestCase):
    def test_uses_configured_api_base_url(self) -> None:
        settings = Settings(
            telegram_bot_token="test-token",
            api_base_url="http://localhost:8000",
        )

        client = create_api_client(settings)

        self.assertIsInstance(client, Client)