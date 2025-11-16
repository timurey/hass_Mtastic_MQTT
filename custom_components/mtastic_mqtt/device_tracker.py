"""Device tracker platform for Meshtastic MQTT integration."""
from __future__ import annotations

from typing import Any
from homeassistant.components import device_tracker
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import BaseEntity, Coordinator
from .constants import DOMAIN

import logging

_LOGGER = logging.getLogger(__name__)

# Conversion factor for latitude/longitude (degrees * 1e7)
LAT_LON_SCALE = 10000000.0


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up device tracker from a config entry."""
    coordinator: Coordinator = entry.runtime_data
    async_add_entities([PositionTracker(coordinator)])
    _LOGGER.debug("Added position device tracker")


class PositionTracker(BaseEntity, device_tracker.TrackerEntity):
    """Device tracker for position."""

    def __init__(self, coordinator: Coordinator) -> None:
        """Initialize device tracker."""
        super().__init__(coordinator)
        self.with_name("position_tracker", "Position")
        self._attr_entity_category = None

    @property
    def latitude(self) -> float | None:
        """Return latitude."""
        if pos := self.coordinator.data.get("position"):
            if value := pos.get("latitude_i"):
                try:
                    return float(value) / LAT_LON_SCALE
                except (ValueError, TypeError) as err:
                    _LOGGER.warning("Invalid latitude value: %s", err)
        return None

    @property
    def longitude(self) -> float | None:
        """Return longitude."""
        if pos := self.coordinator.data.get("position"):
            if value := pos.get("longitude_i"):
                try:
                    return float(value) / LAT_LON_SCALE
                except (ValueError, TypeError) as err:
                    _LOGGER.warning("Invalid longitude value: %s", err)
        return None

    @property
    def battery_level(self) -> int | None:
        """Return battery level."""
        if tel := self.coordinator.data.get("device_metrics"):
            if (value := tel.get("battery_level", 0)) > 0:
                try:
                    return int(value)
                except (ValueError, TypeError):
                    pass
        return None

    @property
    def source_type(self) -> device_tracker.SourceType | str:
        """Return the source type."""
        return device_tracker.SourceType.GPS

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        result: dict[str, Any] = {}
        if pos := self.coordinator.data.get("position"):
            for attr in ("altitude", "ground_speed", "sats_in_view"):
                if value := pos.get(attr):
                    try:
                        result[attr] = float(value) if attr in ("altitude", "ground_speed") else int(value)
                    except (ValueError, TypeError):
                        _LOGGER.debug("Invalid value for %s: %s", attr, value)
        return result
