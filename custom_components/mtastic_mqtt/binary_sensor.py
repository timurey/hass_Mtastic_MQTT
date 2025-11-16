"""Binary sensor platform for Meshtastic MQTT integration."""
from __future__ import annotations

from typing import Any
from homeassistant.components import binary_sensor
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import BaseEntity, Coordinator
from .constants import DOMAIN

import logging

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up binary sensors from a config entry."""
    coordinator: Coordinator = entry.runtime_data
    
    # Only add online sensor if stat_topic is configured
    if coordinator._stat_subs:
        async_add_entities([OnlineBinarySensor(coordinator)])
        _LOGGER.debug("Added online binary sensor")
    else:
        _LOGGER.debug("Skipping online binary sensor (no stat_topic configured)")


class OnlineBinarySensor(BaseEntity, binary_sensor.BinarySensorEntity):
    """Binary sensor for online status."""

    def __init__(self, coordinator: Coordinator) -> None:
        """Initialize binary sensor."""
        super().__init__(coordinator)
        self.with_name("online", "Online")
        self._attr_device_class = binary_sensor.BinarySensorDeviceClass.CONNECTIVITY

    @property
    def is_on(self) -> bool | None:
        """Return the state of the binary sensor."""
        if stat := self.coordinator.data.get("stat"):
            if isinstance(stat, str):
                return stat.lower() == "online"
            return stat == "online"
        return None
