"""The Meshtastic MQTT integration."""
from __future__ import annotations

from typing import Any
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType

from .constants import DOMAIN, PLATFORMS
from .coordinator import Coordinator, Platform

import voluptuous as vol
import logging

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema({}, extra=vol.ALLOW_EXTRA),
    },
    extra=vol.ALLOW_EXTRA,
)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Meshtastic MQTT integration."""
    platform = Platform(hass)
    await platform.async_load()
    hass.data[DOMAIN] = platform
    _LOGGER.debug("Platform initialized")
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Meshtastic MQTT from a config entry."""
    _LOGGER.debug("Setting up entry: %s", entry.entry_id)
    
    platform: Platform = hass.data[DOMAIN]
    coordinator = Coordinator(platform, entry)
    entry.runtime_data = coordinator
    
    try:
        await coordinator.async_load()
        await coordinator.async_config_entry_first_refresh()
    except Exception as err:
        _LOGGER.error("Failed to load coordinator: %s", err)
        return False
    
    entry.async_on_unload(entry.add_update_listener(_async_update_entry))
    
    try:
        await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
        _LOGGER.info("Successfully set up entry for node %s", entry.title)
        return True
    except Exception as err:
        _LOGGER.error("Failed to set up platforms: %s", err)
        await coordinator.async_unload()
        return False


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    _LOGGER.debug("Unloading entry: %s", entry.entry_id)
    
    coordinator: Coordinator = entry.runtime_data
    
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        await coordinator.async_unload()
        entry.runtime_data = None
        _LOGGER.debug("Successfully unloaded entry")
    else:
        _LOGGER.warning("Failed to unload some platforms")
    
    return unload_ok


async def _async_update_entry(
    hass: HomeAssistant, entry: ConfigEntry
) -> None:
    """Handle options update."""
    _LOGGER.debug("Updating entry: %s", entry.entry_id)
    
    coordinator: Coordinator = entry.runtime_data
    
    try:
        await coordinator.async_unload()
        await coordinator.async_load()
        _LOGGER.debug("Entry updated successfully")
    except Exception as err:
        _LOGGER.error("Failed to update entry: %s", err)
