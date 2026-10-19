"""Coordinator for EV-ES Cloud updates."""

from __future__ import annotations

import logging

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import EvesCloudApiError, EvesCloudAuthenticationError, EvesCloudClient, EvesCloudSubscriptionError
from .const import DOMAIN, UPDATE_INTERVAL

_LOGGER = logging.getLogger(__name__)


class EvesCloudCoordinator(DataUpdateCoordinator[dict[str, dict]]):
    """Fetch all latest device values in one HTTPS request."""

    def __init__(self, hass: HomeAssistant, client: EvesCloudClient) -> None:
        super().__init__(hass, logger=_LOGGER, name=DOMAIN, update_interval=UPDATE_INTERVAL)
        self.client = client

    async def _async_update_data(self) -> dict[str, dict]:
        try:
            response = await self.client.async_get_devices()
        except EvesCloudAuthenticationError as err:
            raise ConfigEntryAuthFailed from err
        except EvesCloudSubscriptionError as err:
            raise UpdateFailed("EV-ES Cloud subscription is inactive") from err
        except EvesCloudApiError as err:
            raise UpdateFailed(str(err)) from err
        payload = response.get("data", {})
        devices = payload.get("devices", []) if isinstance(payload, dict) else []
        return {
            str(device["serial_number"]): device
            for device in devices
            if isinstance(device, dict) and device.get("serial_number")
        }

    async def async_command(self, serial_number: str, action: str, **data) -> None:
        """Queue a command without treating it as an immediate telemetry update."""
        await self.client.async_command(action, serial_number, **data)
