"""Shared EV-ES Cloud entity base."""

from __future__ import annotations

from typing import Any

from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .coordinator import EvesCloudCoordinator
from .const import DOMAIN
from .api import EvesCloudApiError


class EvesCloudEntity(CoordinatorEntity[EvesCloudCoordinator]):
    """Entity backed by one EV-BPM item in the shared coordinator."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: EvesCloudCoordinator, serial: str) -> None:
        super().__init__(coordinator)
        self._serial = serial

    @property
    def device_data(self) -> dict[str, Any] | None:
        return self.coordinator.data.get(self._serial)

    @property
    def available(self) -> bool:
        return self.device_data is not None and self.coordinator.last_update_success

    @property
    def device_info(self) -> DeviceInfo:
        data = self.device_data or {}
        return DeviceInfo(
            identifiers={(DOMAIN, self._serial)},
            name=str(data.get("friendly_name") or self._serial),
            manufacturer="EV-ES",
            model="EV-BPM",
            serial_number=self._serial,
            sw_version=str(data.get("firmware_version") or "") or None,
        )

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        data = self.device_data or {}
        return {
            "serial_number": self._serial,
            "group": data.get("group"),
            "shared": data.get("shared", False),
            "last_seen_at": data.get("last_seen_at"),
            "device_state": data.get("device_state"),
            "battery_state": data.get("battery_state"),
            "active_errors": data.get("active_errors", []),
            "last_errors": data.get("last_errors", []),
            "local_ip_address": data.get("local_ip_address"),
        }

    async def async_queue_command(self, action: str, **data: Any) -> None:
        """Queue a Cloud command and translate API failures to HA errors."""
        try:
            await self.coordinator.async_command(self._serial, action, **data)
        except EvesCloudApiError as err:
            raise HomeAssistantError(str(err)) from err
