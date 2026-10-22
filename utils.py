"""Utilities for FranklinWH integration."""

import franklinwh
import franklinwh_direct_or_cloud
import httpx

from homeassistant.core import HomeAssistant
from homeassistant.helpers.httpx_client import (
    SSL_ALPN_HTTP11_HTTP2,
    create_async_httpx_client,
)

from .data import MessageStats


class MessageStatsClient(franklinwh_direct_or_cloud.Client):
    """Client for fetching messages from FranklinWH."""

    async def get_message_stats(self) -> MessageStats:
        """Fetch message statistics from FranklinWH."""
        unread = await self.get_unread_message_count()
        return MessageStats(
            unread=unread,
        )


async def get_client(
    hass: HomeAssistant,
    username: str,
    password: str,
    gateway_id: str,
) -> tuple[franklinwh.TokenFetcher, MessageStatsClient]:
    """Create a franklinwh TokenFetcher and Client."""

    def _get_client() -> httpx.AsyncClient:
        return create_async_httpx_client(hass, alpn_protocols=SSL_ALPN_HTTP11_HTTP2)

    franklinwh.HttpClientFactory.set_client_factory(_get_client)
    token_fetcher = franklinwh.TokenFetcher(username, password)
    client = MessageStatsClient(token_fetcher, gateway_id, direct_connect_host="172.17.0.1")
    await client.refresh_token()
    return (token_fetcher, client)
