"""Data coordinator for Meshtastic MQTT integration."""
from __future__ import annotations

from typing import Any, Callable
from datetime import datetime

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)
from homeassistant.exceptions import HomeAssistantError
from homeassistant.components.mqtt import client as mqtt_client
from homeassistant.components.mqtt.models import ReceiveMessage
from homeassistant.util import dt
from homeassistant.helpers import storage

from .protobuf import mesh_pb2, mqtt_pb2, portnums_pb2, telemetry_pb2
from .constants import DOMAIN
from .proto import convert_envelope_to_json, try_encrypt_envelope

import logging

_LOGGER = logging.getLogger(__name__)


class Platform:
    """Platform data storage manager."""

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize platform storage."""
        self.hass = hass
        self._storage = storage.Store(hass, 1, DOMAIN)
        self._storage_data: dict[str, Any] = {}

    async def async_load(self) -> None:
        """Load stored data."""
        data = await self._storage.async_load()
        _LOGGER.debug("Loaded stored data: %s", data)
        self._storage_data = data if data else {}

    def get_data(self, key: str, default: dict[str, Any] | None = None) -> dict[str, Any]:
        """Get data for a key."""
        if default is None:
            default = {}
        return self._storage_data.get(key, default)

    async def async_put_data(self, key: str, data: dict[str, Any] | None) -> None:
        """Store data for a key."""
        if data:
            self._storage_data = {
                **self._storage_data,
                key: data,
            }
        else:
            self._storage_data.pop(key, None)
        await self._storage.async_save(self._storage_data)


class Coordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Data coordinator for Meshtastic MQTT node."""

    def __init__(self, platform: Platform, entry: ConfigEntry) -> None:
        """Initialize coordinator."""
        super().__init__(
            platform.hass,
            _LOGGER,
            name=f"{DOMAIN}_{entry.entry_id}",
            update_interval=None,  # Updates come via MQTT, not polling
        )
        self._platform = platform
        self._entry = entry
        self._entry_id = entry.entry_id
        self._config: dict[str, Any] = {}
        self._node_id = ""
        self._id = 0
        self._data_subs: Callable[[], None] | None = None
        self._stat_subs: Callable[[], None] | None = None

    async def _async_update_data(self) -> dict[str, Any]:
        """Update data from storage."""
        return self._platform.get_data(self._entry_id)

    async def _async_update_state(self, data: dict[str, Any]) -> None:
        """Update coordinator state."""
        self.async_set_updated_data({
            **self.data,
            **data,
        })
        await self._platform.async_put_data(self._entry_id, self.data)

    async def async_load(self) -> None:
        """Load coordinator configuration and subscribe to MQTT topics."""
        self._config = self._entry.as_dict()["options"]
        self._node_id = self._config.get("id", "")
        if not self._node_id:
            raise HomeAssistantError("Node ID is required")
        
        try:
            self._id = int(self._node_id[1:], 16)
        except (ValueError, IndexError) as err:
            raise HomeAssistantError(f"Invalid node ID format: {self._node_id}") from err

        _LOGGER.debug(
            "Loading coordinator for node %s (ID: %d), config: %s",
            self._node_id,
            self._id,
            self._config,
        )

        pb_topic = self._config.get("pb_topic")
        if not pb_topic:
            raise HomeAssistantError("Protobuf topic (pb_topic) is required")

        try:
            self._data_subs = await mqtt_client.async_subscribe(
                self.hass,
                pb_topic,
                self._async_on_pb_message,
                encoding=None,
            )
            _LOGGER.info("Subscribed to protobuf topic: %s", pb_topic)
        except Exception as err:
            _LOGGER.error("Failed to subscribe to protobuf topic %s: %s", pb_topic, err)
            raise HomeAssistantError(f"Failed to subscribe to MQTT topic: {pb_topic}") from err

        stat_topic = self._config.get("stat_topic")
        if stat_topic:
            try:
                self._stat_subs = await mqtt_client.async_subscribe(
                    self.hass,
                    stat_topic,
                    self._async_on_stat_message,
                )
                _LOGGER.info("Subscribed to status topic: %s", stat_topic)
            except Exception as err:
                _LOGGER.warning("Failed to subscribe to status topic %s: %s", stat_topic, err)

    async def async_unload(self) -> None:
        """Unload coordinator and unsubscribe from MQTT topics."""
        _LOGGER.debug("Unloading coordinator for node %s", self._node_id)
        
        if self._data_subs:
            self._data_subs()
            self._data_subs = None
        
        if self._stat_subs:
            self._stat_subs()
            self._stat_subs = None

    async def _async_process_message(self, obj: dict[str, Any]) -> None:
        """Process a decoded message."""
        _LOGGER.debug("Processing message for node %d: %s", self._id, obj)
        
        if "type" not in obj or "payload" not in obj:
            _LOGGER.debug("Message missing type or payload, skipping")
            return

        if obj.get("from") != self._id:
            _LOGGER.debug("Ignoring relay message from node %s", obj.get("from"))
            return

        type_ = obj["type"]
        payload = {
            **self.data.get(type_, {}),
            **obj["payload"],
        }

        # Ignore nodeinfo about other nodes
        if type_ == "nodeinfo" and obj.get("sender") != payload.get("id"):
            _LOGGER.debug("Ignoring nodeinfo about other node")
            return

        dt_now = dt.now()
        await self._async_update_state({
            type_: payload,
            "last_update": dt_now.timestamp(),
        })

    async def _async_on_pb_message(self, message: ReceiveMessage) -> None:
        """Handle protobuf MQTT message."""
        _LOGGER.debug("Received protobuf message on topic %s", message.topic)
        
        try:
            env = mqtt_pb2.ServiceEnvelope()
            env.ParseFromString(message.payload)
            _LOGGER.debug("Parsed envelope: %s", env)
            
            if env.packet.HasField("encrypted"):
                encryption_key = self._config.get("key", "AQ==")
                try:
                    try_encrypt_envelope(env, encryption_key)
                    _LOGGER.debug("Decrypted packet successfully")
                except Exception as err:
                    _LOGGER.warning("Failed to decrypt packet: %s", err)
                    return

            obj = convert_envelope_to_json(env)
            _LOGGER.debug("Converted to JSON: %s", obj)
            await self._async_process_message(obj)
            
        except Exception as err:
            _LOGGER.exception("Error parsing protobuf message: %s", err)

    async def _async_on_stat_message(self, message: ReceiveMessage) -> None:
        """Handle status MQTT message."""
        _LOGGER.debug("Received status message: %s", message.payload)
        
        try:
            stat_value = message.payload.decode("utf-8") if isinstance(message.payload, bytes) else message.payload
            await self._async_update_state({
                "stat": stat_value,
            })
        except Exception as err:
            _LOGGER.exception("Error processing status message: %s", err)

    @property
    def last_update(self) -> datetime | None:
        """Get last update timestamp."""
        if "last_update" in self.data:
            try:
                return datetime.fromtimestamp(
                    self.data["last_update"],
                    tz=dt.DEFAULT_TIME_ZONE,
                )
            except (ValueError, OSError) as err:
                _LOGGER.warning("Invalid timestamp in data: %s", err)
        return None


class BaseEntity(CoordinatorEntity[Coordinator]):
    """Base entity for Meshtastic MQTT entities."""

    def __init__(self, coordinator: Coordinator) -> None:
        """Initialize base entity."""
        super().__init__(coordinator)

    def with_name(self, entity_id: str, name: str) -> "BaseEntity":
        """Configure entity name and unique ID."""
        self._attr_has_entity_name = True
        self._attr_unique_id = f"{DOMAIN}_{self.coordinator._entry_id}_{entity_id}"
        self._attr_name = name
        return self

    @property
    def device_info(self) -> dict[str, Any]:
        """Return device information."""
        node_info = self.coordinator.data.get("nodeinfo", {})
        return {
            "identifiers": {(DOMAIN, self.coordinator._entry_id)},
            "name": self.coordinator._entry.title,
            "manufacturer": "Meshtastic",
            "model": "MQTT Node",
            "sw_version": node_info.get("longname", ""),
        }
