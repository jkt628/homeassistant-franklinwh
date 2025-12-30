"""Utilities for FranklinWH integration."""

import franklinwh
import httpx

from homeassistant.core import HomeAssistant
from homeassistant.helpers.httpx_client import (
    SSL_ALPN_HTTP11_HTTP2,
    create_async_httpx_client,
)


async def get_client(
    hass: HomeAssistant,
    username: str,
    password: str,
    gateway_id: str,
) -> tuple[franklinwh.TokenFetcher, franklinwh.Client]:
    """Create a franklinwh TokenFetcher and Client."""

    def _get_client() -> httpx.AsyncClient:
        return create_async_httpx_client(hass, alpn_protocols=SSL_ALPN_HTTP11_HTTP2)

    franklinwh.HttpClientFactory.set_client_factory(_get_client)
    token_fetcher = franklinwh.TokenFetcher(username, password)
    client = franklinwh.Client(token_fetcher, gateway_id)
    await client.refresh_token()
    return (token_fetcher, client)
