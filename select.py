"""Select platform for FranklinWH integration."""

from franklinwh.client import WorkMode

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER, MODEL
from .coordinator import FranklinWHCoordinator


class ModeEnabledEntity(CoordinatorEntity[FranklinWHCoordinator], Entity):
    """Base class for entities that require the mode to be enabled on coordinator."""

    _unique_id_suffix: str

    @classmethod
    async def async_setup_entry(
        cls,
        hass: HomeAssistant,
        entry: ConfigEntry,
        async_add_entities: AddConfigEntryEntitiesCallback,
    ) -> None:
        """Set up FranklinWH selectors."""
        coordinators: dict[str, FranklinWHCoordinator] = hass.data[DOMAIN][
            entry.entry_id
        ]
        for subentry_id, sub in entry.subentries.items():
            assert sub.unique_id is not None
            coordinator = coordinators[sub.unique_id]
            coordinator.enable("mode")
            async_add_entities(
                [cls(coordinator, entry)], config_subentry_id=subentry_id
            )

    def __init__(
        self,
        coordinator: FranklinWHCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the mode enabled entity."""
        super().__init__(coordinator)

        gateway_id = coordinator.client.gateway
        self._attr_unique_id = f"{gateway_id}{self._unique_id_suffix}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, gateway_id)},
            name=f"FranklinWH {gateway_id[-6:]}",
            manufacturer=MANUFACTURER,
            model=MODEL,
            sw_version=entry.data.get("sw_version"),
        )


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up FranklinWH selectors."""
    await ModeSelect.async_setup_entry(hass, entry, async_add_entities)


class ModeSelect(ModeEnabledEntity, SelectEntity):
    """Representation of the FranklinWH operating mode."""

    _attr_has_entity_name = True
    _attr_name = "Operating Mode"
    _unique_id_suffix = "_mode"
    _attr_options = list(WorkMode.titles())
    _icons = {
        WorkMode.TIME_OF_USE.title: "mdi:battery-clock",
        WorkMode.SELF_CONSUMPTION.title: "mdi:battery-arrow-down",
        WorkMode.EMERGENCY_BACKUP.title: "mdi:battery-arrow-up",
        WorkMode.DEBUG.title: "mdi:bug",
        WorkMode.GENERATOR.title: "mdi:generator-stationary",
        WorkMode.VPP_MODE.title: "mdi:battery-heart",
        None: "mdi:battery-alert",
    }
    assert set(_icons.keys()) == set(_attr_options) | {None}

    @property
    def current_option(self) -> str | None:
        """Return the current selected option."""
        if self.coordinator.data is None or self.coordinator.data.mode is None:
            return None
        return WorkMode.from_id(self.coordinator.data.mode.workMode).title

    @property
    def icon(self) -> str:
        """Return the icon for the select."""
        return self._icons[self.current_option]

    async def async_select_option(self, option: str) -> None:
        """Handle option selection."""
        await self.coordinator.async_set_mode(option)
