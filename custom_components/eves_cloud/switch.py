"""Switch entities for EV-ES Cloud controls."""

from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import EvesCloudConfigEntry
from .entity import EvesCloudEntity


async def async_setup_entry(hass, entry: EvesCloudConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    """Add battery and balancing switches."""
    coordinator = entry.runtime_data.coordinator
    async_add_entities(
        EvesCloudSwitch(coordinator, serial, control)
        for serial in coordinator.data
        for control in ("battery_enabled", "balancing_enabled")
    )


class EvesCloudSwitch(EvesCloudEntity, SwitchEntity):
    """A queued EV-BPM switch command."""

    def __init__(self, coordinator, serial: str, control: str) -> None:
        super().__init__(coordinator, serial)
        self._control = control
        self._attr_unique_id = f"{serial}_{control}_control"
        self._attr_name = "Battery enabled" if control == "battery_enabled" else "Balancing enabled"
        self._attr_icon = "mdi:battery-check" if control == "battery_enabled" else "mdi:scale-balance"

    @property
    def available(self) -> bool:
        data = self.device_data
        if not super().available or not data or data.get("online") is not True:
            return False
        if self._control == "battery_enabled":
            return data.get("battery_enabled") is not None
        return (
            data.get("is_owner") is True
            and data.get("config_can_balance") is True
            and data.get("config_balancing_enabled") is not None
        )

    @property
    def is_on(self) -> bool | None:
        data = self.device_data
        if data is None:
            return None
        key = "battery_enabled" if self._control == "battery_enabled" else "config_balancing_enabled"
        value = data.get(key)
        return None if value is None else bool(value)

    async def async_turn_on(self, **kwargs) -> None:
        """Enable the selected feature."""
        if self._control == "battery_enabled":
            await self.async_queue_command("battery.set_enabled", enabled=True)
        else:
            await self.async_queue_command("configuration.update", changes={"balance_enabled": True})

    async def async_turn_off(self, **kwargs) -> None:
        """Disable the selected feature."""
        if self._control == "battery_enabled":
            await self.async_queue_command("battery.set_enabled", enabled=False)
        else:
            await self.async_queue_command("configuration.update", changes={"balance_enabled": False})
