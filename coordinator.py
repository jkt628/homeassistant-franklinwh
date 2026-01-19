"""DataUpdateCoordinator for FranklinWH."""

import asyncio
from dataclasses import dataclass
from datetime import timedelta
import logging
import sys
from typing import Any, Final

from franklinwh import Client, GridStatus, Mode, Stats

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DEFAULT_LOCAL_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL, DOMAIN
from .utils import get_client


@dataclass
class FranklinWHData:
    """Statistics for FranklinWH."""

    stats: Stats | None = None
    switch_state: tuple[bool, bool, bool] | None = None


class FranklinWHCoordinator(DataUpdateCoordinator[FranklinWHData]):
    """Fetch FranklinWH data.

    This class always produces stats and optionally other attributes when enabled.
    """

    _data: Final = {
        "stats": "get_stats",
        "switch_state": "get_smart_switch_state",
    }

    @staticmethod
    async def disabled() -> None:
        """Placeholder for disabled method."""
        return

    def __init__(
        self,
        *,
        hass: HomeAssistant,
        username: str,
        password: str,
        gateway_id: str,
        use_local_api: bool = False,
        local_host: str | None = None,
        max_failures: int = 3,
    ) -> None:
        """Initialize the coordinator."""
        if max_failures == -1:
            max_failures = sys.maxsize
        elif max_failures > 60:
            raise ValueError("max_failures must be between-1 (infinite) and 60")

        # Set update interval based on API type
        update_interval = (
            DEFAULT_LOCAL_SCAN_INTERVAL if use_local_api else DEFAULT_SCAN_INTERVAL
        )

        super().__init__(
            hass,
            logging.getLogger(DOMAIN),
            name=DOMAIN,
            update_interval=timedelta(seconds=update_interval),
            # Keep entities available during temporary failures
            # Only mark unavailable after 3 consecutive failures (3 minutes)
            always_update=False,
        )

        # Store credentials for lazy client initialization
        self.username = username
        self.password = password
        self.gateway_id = gateway_id
        self.use_local_api = use_local_api
        self.local_host = local_host
        self.client: Client = None  # type: ignore  # noqa: PGH003
        self._client_lock = asyncio.Lock()

        # Track consecutive failures
        self._consecutive_failures = 0
        self._max_failures = max_failures

        # Track dynamic stats
        self._methods = [self.disabled for _ in self._data]
        self._enabled = []

    def enable(self, attr: str) -> None:
        """Produce an attribute during data fetch."""
        if attr not in self._data:
            raise ValueError(f"Attribute '{attr}' is not a valid data attribute")
        if attr not in self._enabled:
            self._enabled.append(attr)
        for i, k in enumerate(self._data):
            if k in self._enabled:
                self._methods[i] = getattr(self.client, self._data[k])

    async def _async_update_data(self) -> FranklinWHData:
        """Fetch data from FranklinWH API."""
        try:
            # Initialize client on first run (in executor to avoid blocking)
            if self.client is None:
                async with self._client_lock:
                    try:
                        _, self.client = await get_client(
                            self.hass,
                            self.username,
                            self.password,
                            self.gateway_id,
                        )
                    except Exception as err:
                        raise UpdateFailed(
                            f"Failed to initialize client: {err}"
                        ) from err
                    self.enable("stats")

            # Fetch data attributes
            tasks = [function() for function in self._methods]
            results = await asyncio.gather(*tasks)

            # Reset failure counter on success
            self._consecutive_failures = 0

            return FranklinWHData(*results)

        except Exception as err:
            text = str(err).lower()
            # Check if it's an authentication-related error
            if "auth" in text or "token" in text:
                raise ConfigEntryAuthFailed(f"Authentication failed: {err}") from err

            # Increment failure counter
            self._consecutive_failures += 1
            self.logger.warning(
                "API error (attempt %d/%d): %s",
                self._consecutive_failures,
                self._max_failures,
                err,
            )

            # Only raise UpdateFailed after max failures
            if self._consecutive_failures >= self._max_failures:
                self.logger.error(
                    "Max consecutive failures reached, marking unavailable"
                )
                self.client = None  # force reinitialization on next update
                raise UpdateFailed(f"Error communicating with API: {err}") from err

            # Return last known data to keep entities available
            if self.data:
                self.logger.debug("Returning last known data due to temporary failure")
                return self.data
            raise UpdateFailed(f"Error communicating with API: {err}") from err

    async def async_set(self, func, *args: Any, **kwargs: Any) -> None:
        """Generic setter to call client methods and refresh data."""
        sleep = kwargs.pop("sleep", 7)
        value = kwargs.pop("value", "value")
        try:
            await func(*args, **kwargs)
            await asyncio.sleep(sleep)
            await self.async_request_refresh()
        except Exception as err:
            self.logger.error("Failed to set %s: %s", value, err)
            raise

    async def async_set_generator(self, enabled: bool) -> None:
        """Set the generator."""
        await self.async_set(self.client.set_generator, enabled, value="generator")

    async def async_set_grid_status(self, status: GridStatus) -> None:
        """Set the grid connection."""
        await self.async_set(self.client.set_grid_status, status, value="grid status")

    async def async_set_switch_state(self, switches: tuple[bool, bool, bool]) -> None:
        """Set the state of smart switches."""
        await self.async_set(
            self.client.set_smart_switch_state, switches, value="switch state", sleep=1
        )

    async def async_set_operation_mode(self, mode: str) -> None:
        """Set the operation mode of the system."""
        try:
            # Map string mode to Mode factory methods
            # Each mode gets a default reserve of 20% except emergency_backup (100%)
            mode_map = {
                "self_use": Mode.self_consumption,
                "backup": Mode.emergency_backup,
                "time_of_use": Mode.time_of_use,
                # Note: clean_backup mode from Home Assistant services.yaml
                # Maps to emergency_backup as the library doesn't have a separate clean_backup mode
                "clean_backup": Mode.emergency_backup,
            }

            if mode not in mode_map:
                raise ValueError(f"Invalid mode: {mode}")

            # Create mode object with default SOC
            mode_obj = mode_map[mode]()

            # Set the mode via API (async method in franklinwh 1.0.0+)
            await self.client.set_mode(mode_obj)

            # Request immediate refresh
            await self.async_request_refresh()
            self.logger.info("Successfully set operation mode to %s", mode)
        except Exception as err:
            self.logger.error("Failed to set operation mode to %s: %s", mode, err)
            raise

    async def async_set_battery_reserve(self, reserve_percent: int) -> None:
        """Set the battery reserve percentage.

        This attempts to preserve the current operation mode while updating
        the battery reserve (SOC) percentage. If the current mode cannot be
        determined, it defaults to self_consumption mode.
        """
        try:
            # Try to get the current mode to preserve it (async method in franklinwh 1.0.0+)
            try:
                current_mode = await self.client.get_mode()
                self.logger.debug("Current mode retrieved: %s", current_mode)
            except Exception as err:
                self.logger.warning(
                    "Could not retrieve current mode, defaulting to self_consumption: %s",
                    err,
                )
                current_mode = None

            # Create new mode with updated SOC
            # Note: We need to detect the current mode type to preserve it
            # For now, we default to self_consumption if we can't determine the mode
            # TODO: Add mode type detection when the API provides mode information
            mode_obj = Mode.self_consumption(soc=reserve_percent)

            # Async method in franklinwh 1.0.0+
            await self.client.set_mode(mode_obj)

            # Request immediate refresh
            await self.async_request_refresh()
            self.logger.info(
                "Successfully set battery reserve to %d%%", reserve_percent
            )
        except Exception as err:
            self.logger.error(
                "Failed to set battery reserve to %d%%: %s", reserve_percent, err
            )
            raise
