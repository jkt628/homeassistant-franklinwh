"""Number platform for FranklinWH integration."""

from homeassistant.components.number import NumberEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .select import ModeEnabledEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up FranklinWH number entities."""
    await BackupReserve.async_setup_entry(hass, entry, async_add_entities)


class BackupReserve(ModeEnabledEntity, NumberEntity):
    """Representation of the FranklinWH backup reserve percentage."""

    _attr_has_entity_name = True
    _attr_name = "Backup Reserve"
    _unique_id_suffix = "_backup_reserve"
    _attr_min_value = 5  # pyright: ignore[reportAssignmentType]
    _attr_max_value = 100  # pyright: ignore[reportAssignmentType]
    _attr_step = 1  # pyright: ignore[reportAssignmentType]
    _attr_unit_of_measurement = "%"  # pyright: ignore[reportAssignmentType]

    @property
    def native_value(self) -> float | None:
        """Return the current backup reserve percentage."""
        if self.coordinator.data is None or self.coordinator.data.mode is None:
            return None
        return self.coordinator.data.mode.soc

    @property
    def icon(self) -> str:
        """Return the icon for the backup reserve percentage."""
        value = self.value
        if value is None:
            return "mdi:battery-alert"
        if value >= 99:
            return "mdi:battery"
        if value < 10:
            return "mdi:battery-outline"
        return "mdi:battery-" + str(int(value // 10 * 10))

    async def async_set_native_value(self, value: float) -> None:
        """Set the backup reserve percentage."""
        await self.coordinator.async_set_backup_reserve(int(value))
