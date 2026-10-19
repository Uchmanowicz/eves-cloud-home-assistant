"""Button entities for EV-ES Cloud actions."""

from __future__ import annotations

from homeassistant.components.button import ButtonDeviceClass, ButtonEntity
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import EvesCloudConfigEntry
from .entity import EvesCloudEntity


async def async_setup_entry(hass, entry: EvesCloudConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    """Add device action buttons."""
    coordinator = entry.runtime_data.coordinator
    async_add_entities(
        EvesCloudActionButton(coordinator, serial, action)
        for serial in coordinator.data
        for action in BUTTON_ACTIONS
    )


BUTTON_ACTIONS = (
    ("reset_device", "Reset device", "mdi:restart", "device.reset", ButtonDeviceClass.RESTART),
    ("check_firmware_updates", "Check for firmware updates", "mdi:cloud-search", "firmware.check_updates", None),
    ("update_firmware", "Update firmware", "mdi:package-up", "firmware.update", ButtonDeviceClass.UPDATE),
    ("calibrate_adc_sensors", "Calibrate ADC sensors", "mdi:meter-electric", "sensor.calibrate_adc", None),
)


class EvesCloudActionButton(EvesCloudEntity, ButtonEntity):
    """Queue one supported signed EV-BPM action."""

    def __init__(self, coordinator, serial: str, action) -> None:
        super().__init__(coordinator, serial)
        key, name, icon, command, device_class = action
        self._command = command
        self._attr_unique_id = f"{serial}_{key}"
        self._attr_name = name
        self._attr_icon = icon
        self._attr_device_class = device_class

    @property
    def available(self) -> bool:
        data = self.device_data
        if not super().available or not data or data.get("online") is not True:
            return False
        if self._command == "device.reset":
            return True
        if data.get("is_owner") is not True:
            return False
        if self._command == "firmware.update":
            return data.get("config_firmware_update_available") is True
        if self._command == "sensor.calibrate_adc":
            return data.get("config_can_calibrate_adc") is True
        return True

    async def async_press(self) -> None:
        """Queue the action; the BPM acknowledges it through Cloud."""
        await self.async_queue_command(self._command)
