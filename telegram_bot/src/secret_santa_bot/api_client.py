
import httpx

from secret_santa_bot.config import Settings
from secret_santa_bot.generated_client.secret_santa_api_client import Client


def create_api_client(settings: Settings) -> Client:
    http_client = httpx.AsyncClient(base_url=settings.api_base_url)
    return Client(base_url=settings.api_base_url).set_async_httpx_client(
        http_client
    )
