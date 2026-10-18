"""EV-ES Cloud integration setup."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import EvesCloudClient
from .const import CONF_BASE_URL, CONF_TOKEN, PLATFORMS
from .coordinator import EvesCloudCoordinator


@dataclass
class EvesCloudRuntimeData:
    """Runtime objects shared by entity platforms."""

    coordinator: EvesCloudCoordinator


EvesCloudConfigEntry = ConfigEntry[EvesCloudRuntimeData]


async def async_setup_entry(hass: HomeAssistant, entry: EvesCloudConfigEntry) -> bool:
    """Set up EV-ES Cloud from a config entry."""
    client = EvesCloudClient(
        async_get_clientsession(hass),
        str(entry.data[CONF_BASE_URL]),
        str(entry.data[CONF_TOKEN]),
    )
    coordinator = EvesCloudCoordinator(hass, client)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = EvesCloudRuntimeData(coordinator)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: EvesCloudConfigEntry) -> bool:
    """Unload EV-ES Cloud entities."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
