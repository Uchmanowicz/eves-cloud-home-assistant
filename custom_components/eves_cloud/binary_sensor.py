"""Binary sensor entities for EV-ES Cloud."""

from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorDeviceClass, BinarySensorEntity
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import EvesCloudConfigEntry
from .entity import EvesCloudEntity

BINARY_SENSORS = (
    ("online", "Online", BinarySensorDeviceClass.CONNECTIVITY),
    ("is_balancing", "Balancing", None),
    ("contactor_negative", "Negative contactor", None),
    ("contactor_positive", "Positive contactor", None),
    ("contactor_precharge", "Precharge contactor", None),
    ("config_can_balance", "Balancing supported", None),
    ("config_can_calibrate_adc", "ADC calibration supported", None),
    ("config_firmware_update_available", "Firmware update available", None),
)


async def async_setup_entry(hass, entry: EvesCloudConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    """Add all current EV-BPM binary sensor entities."""
    coordinator = entry.runtime_data.coordinator
    async_add_entities(
        EvesCloudBinarySensor(coordinator, serial, key, name, device_class)
        for serial in coordinator.data
        for key, name, device_class in BINARY_SENSORS
    )


class EvesCloudBinarySensor(EvesCloudEntity, BinarySensorEntity):
    """One boolean state from the latest Cloud update."""

    def __init__(self, coordinator, serial: str, key: str, name: str, device_class) -> None:
        super().__init__(coordinator, serial)
        self._key = key
        self._attr_translation_key = None
        self._attr_name = name
        self._attr_device_class = device_class
        self._attr_unique_id = f"{serial}_{key}"

    @property
    def is_on(self) -> bool | None:
        data = self.device_data
        if data is None:
            return None
        value = data.get(self._key)
        return None if value is None else bool(value)
