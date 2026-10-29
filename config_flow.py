"""Config flow for FranklinWH integration."""

import logging
from typing import Any

import probatio

from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.const import CONF_PASSWORD, CONF_UNIQUE_ID, CONF_USERNAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError
import homeassistant.helpers.config_validation as cv

from .const import (
    CONF_GATEWAY_ID,
    CONF_USE_LOCAL_API,
    DOMAIN,
    MANUFACTURER,
)
from .utils import get_client

_LOGGER = logging.getLogger(DOMAIN)


async def validate_input(
    hass: HomeAssistant, data: dict[str, Any]
) -> list[dict[str, Any]]:
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """
    username = data[CONF_USERNAME]
    password = data[CONF_PASSWORD]

    try:
        _, client = await get_client(
            hass,
            username,
            password,
            "",
        )

        # Try to fetch data to validate credentials and gateway
        gateways = await client.get_home_gateway_list()
    except Exception as err:
        _LOGGER.exception("Unexpected exception")
        error_str = str(err).lower()

        # Check for specific error types
        if "timeout" in error_str or "timed out" in error_str:
            _LOGGER.error("Device timeout - gateway may be offline or unreachable")
            raise CannotConnect(
                "Gateway device timed out. Please verify:\n"
                "1. Gateway is powered on and connected to network\n"
                "2. Gateway ID is correct\n"
                "3. FranklinWH cloud services are online"
            ) from err

        if "auth" in error_str or "token" in error_str or "401" in error_str:
            raise InvalidAuth from err

        if "gateway" in error_str or "device" in error_str:
            raise InvalidGateway from err

        raise CannotConnect from err

    if gateways is None:
        raise CannotConnect("Unable to fetch data from FranklinWH")

    # Return info that you want to store in the config entry.
    return [
        {
            "title": f"{MANUFACTURER} {gateway['id'][-6:]}",
            CONF_GATEWAY_ID: gateway["id"],
        }
        for gateway in gateways
    ]


class FranklinWHConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for FranklinWH."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            self._async_abort_entries_match(user_input)

            try:
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except InvalidGateway:
                errors["base"] = "invalid_gateway"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(
                    title=MANUFACTURER,
                    data=user_input,
                    subentries=[
                        {
                            "subentry_type": "gateway",
                            "data": entry,
                            "title": entry["title"],
                            CONF_UNIQUE_ID: entry[CONF_GATEWAY_ID],
                        }
                        for entry in info
                    ],
                )

        # Build the data schema
        data_schema = probatio.Schema(
            {
                probatio.Required(CONF_USERNAME): cv.string,
                probatio.Required(CONF_PASSWORD): cv.string,
            }
        )

        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )

    async def async_step_reauth(self, entry_data: dict[str, Any]) -> ConfigFlowResult:
        """Handle reauth when credentials are invalid."""
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle reauth confirmation."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Get the existing entry
            entry = self.hass.config_entries.async_get_entry(self.context["entry_id"])  # type: ignore[typeddict-unknown-key]
            if entry is None:
                return self.async_abort(reason="reauth_failed")

            # Combine existing data with new credentials
            data = {**entry.data, **user_input}

            try:
                await validate_input(self.hass, data)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                self.hass.config_entries.async_update_entry(entry, data=data)
                await self.hass.config_entries.async_reload(entry.entry_id)
                return self.async_abort(reason="reauth_successful")

        data_schema = probatio.Schema(
            {
                probatio.Required(CONF_USERNAME): cv.string,
                probatio.Required(CONF_PASSWORD): cv.string,
            }
        )

        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=data_schema,
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: ConfigEntry,
    ) -> FranklinWHOptionsFlow:
        """Get the options flow for this handler."""
        return FranklinWHOptionsFlow()


class FranklinWHOptionsFlow(OptionsFlow):
    """Handle options flow for FranklinWH."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)
        use_local_api = self.config_entry.options.get("use_local_api", False)

        data_schema = probatio.Schema(
            {
                probatio.Optional(
                    CONF_USE_LOCAL_API, default=use_local_api
                ): cv.boolean,
            }
        )
        for sub in self.config_entry.subentries.values():
            gateway_id = sub.unique_id
            data_schema = data_schema.extend(
                {
                    probatio.Optional(
                        gateway_id,
                        description=f"Direct Connect IP Address for {gateway_id}",
                        default=self.config_entry.options.get(gateway_id, ""),
                    ): cv.string
                }
            )

        return self.async_show_form(step_id="init", data_schema=data_schema)


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""


class InvalidGateway(HomeAssistantError):
    """Error to indicate the gateway ID is invalid."""
