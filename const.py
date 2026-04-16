"""Constants for the FranklinWH integration."""

from typing import Final

DOMAIN: Final = "homeassistant-franklinwh"

# Configuration
CONF_GATEWAY_ID: Final = "gateway_id"
CONF_USE_LOCAL_API: Final = "use_local_api"
CONF_LOCAL_HOST: Final = "local_host"

# Default values
DEFAULT_NAME: Final = "FranklinWH"
DEFAULT_SCAN_INTERVAL: Final = 60  # seconds
DEFAULT_LOCAL_SCAN_INTERVAL: Final = 10  # seconds for local API

# API endpoints (for local API when available)
LOCAL_API_PORT: Final = 8080
LOCAL_API_TIMEOUT: Final = 10

# Device info
MANUFACTURER: Final = "FranklinWH"
MODEL: Final = "aPower/aGate Energy Storage System"
