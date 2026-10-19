"""Select entities for EV-ES Cloud battery configuration."""

from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import EvesCloudConfigEntry
from .entity import EvesCloudEntity


async def async_setup_entry(hass, entry: EvesCloudConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    """Add the Battery ID selector."""
    coordinator = entry.runtime_data.coordinator
    async_add_entities(EvesCloudBatteryIdSelect(coordinator, serial) for serial in coordinator.data)


class EvesCloudBatteryIdSelect(EvesCloudEntity, SelectEntity):
    """Battery CAN ID persisted through a queued configuration command."""

    _attr_name = "Battery ID"
    _attr_icon = "mdi:identifier"
    _attr_options = [str(value) for value in range(1, 17)]

    def __init__(self, coordinator, serial: str) -> None:
        super().__init__(coordinator, serial)
        self._attr_unique_id = f"{serial}_battery_id_control"

    @property
    def available(self) -> bool:
        data = self.device_data
        return bool(
            super().available
            and data
            and data.get("online") is True
            and data.get("is_owner") is True
            and data.get("config_battery_id") is not None
        )

    @property
    def current_option(self) -> str | None:
        data = self.device_data
        value = data.get("config_battery_id") if data else None
        return str(value) if value is not None else None

    async def async_select_option(self, option: str) -> None:
        """Queue a Battery ID change."""
        await self.async_queue_command("configuration.update", changes={"battery_id": int(option)})
