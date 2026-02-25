"""Utilities for FranklinWH integration."""

import franklinwh
import httpx

from homeassistant.const import __short_version__
from homeassistant.core import HomeAssistant


async def get_client(
    hass: HomeAssistant,
    username: str,
    password: str,
    gateway: str,
) -> tuple[franklinwh.TokenFetcher, franklinwh.Client]:
    """Create a franklinwh TokenFetcher and Client."""

    fetcher = franklinwh.TokenFetcher(username, password)
    if __short_version__ >= "2026.2":
        # pylint: disable=no-name-in-module,import-outside-toplevel
        from homeassistant.helpers.httpx_client import (  # noqa: PLC0415
            SSL_ALPN_HTTP11_HTTP2,  # type: ignore  # noqa: PGH003
            create_async_httpx_client,
        )
        # pylint: enable=no-name-in-module,import-outside-toplevel

        def _get_client() -> httpx.AsyncClient:
            return create_async_httpx_client(hass, alpn_protocols=SSL_ALPN_HTTP11_HTTP2)

        franklinwh.HttpClientFactory.set_client_factory(_get_client)
        client = franklinwh.Client(fetcher, gateway)
    else:
        client = await hass.async_add_executor_job(franklinwh.Client, fetcher, gateway)
    return (fetcher, client)
