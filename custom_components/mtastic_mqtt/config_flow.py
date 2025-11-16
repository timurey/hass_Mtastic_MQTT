"""Config flow for Meshtastic MQTT integration."""
from __future__ import annotations

from typing import Any
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.selector import TextSelector, TextSelectorConfig

from .constants import DOMAIN

import voluptuous as vol
import logging

_LOGGER = logging.getLogger(__name__)

# Node ID validation: must start with ! and be 9 characters total
NODE_ID_PATTERN = r"^![0-9a-fA-F]{8}$"


async def _validate_input(hass: HomeAssistant, user_input: dict[str, Any]) -> tuple[str | None, dict[str, Any] | None]:
    """Validate user input."""
    errors: dict[str, str] = {}
    
    # Validate node ID format
    node_id = user_input.get("id", "").strip()
    if not node_id:
        errors["id"] = "node_id_required"
    elif len(node_id) != 9 or node_id[0] != "!":
        errors["id"] = "invalid_node_id_format"
    else:
        try:
            int(node_id[1:], 16)
        except ValueError:
            errors["id"] = "invalid_node_id_hex"
    
    # Validate protobuf topic
    pb_topic = user_input.get("pb_topic", "").strip()
    if not pb_topic:
        errors["pb_topic"] = "pb_topic_required"
    
    # Validate encryption key format if provided
    if key := user_input.get("key", "").strip():
        try:
            import base64
            key_normalized = key.replace("_", "/").replace("-", "+")
            decoded = base64.b64decode(key_normalized.encode("ascii"))
            if len(decoded) != 16 and len(decoded) != 1:
                errors["key"] = "invalid_key_length"
        except Exception:
            errors["key"] = "invalid_key_format"
    
    if errors:
        return list(errors.values())[0], None
    
    return None, user_input


def _create_schema(
    hass: HomeAssistant,
    user_input: dict[str, Any] | None = None,
    flow: str = "config",
) -> vol.Schema:
    """Create configuration schema."""
    if user_input is None:
        user_input = {}
    
    schema_dict: dict[vol.Required | vol.Optional, Any] = {}
    
    if flow == "config":
        schema_dict[vol.Required("title", default=user_input.get("title", ""))] = TextSelector(
            TextSelectorConfig(type="text")
        )
    
    schema_dict[vol.Required("id", default=user_input.get("id", ""))] = TextSelector(
        TextSelectorConfig(type="text", placeholder="!aabbccdd")
    )
    
    schema_dict[vol.Required("pb_topic", default=user_input.get("pb_topic", ""))] = TextSelector(
        TextSelectorConfig(type="text", placeholder="msh/EU_868/2/c/LongFast/!aabbccdd")
    )
    
    schema_dict[vol.Optional("key", default=user_input.get("key", ""))] = TextSelector(
        TextSelectorConfig(type="password", autocomplete="off")
    )
    
    schema_dict[vol.Optional("stat_topic", default=user_input.get("stat_topic", ""))] = TextSelector(
        TextSelectorConfig(type="text", placeholder="msh/EU_868/2/stat/!aabbccdd")
    )
    
    return vol.Schema(schema_dict)


class ConfigFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Meshtastic MQTT."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user",
                data_schema=_create_schema(self.hass),
            )
        
        _LOGGER.debug("User input received: %s", {k: v for k, v in user_input.items() if k != "key"})
        
        error, validated_data = await _validate_input(self.hass, user_input)
        
        if error:
            _LOGGER.warning("Validation error: %s", error)
            return self.async_show_form(
                step_id="user",
                data_schema=_create_schema(self.hass, user_input),
                errors={"base": error},
            )
        
        # Check for duplicate entries (by node ID)
        await self.async_set_unique_id(validated_data["id"])
        self._abort_if_unique_id_configured()
        
        _LOGGER.info("Creating entry for node %s", validated_data["id"])
        return self.async_create_entry(
            title=validated_data.get("title", validated_data["id"]),
            data={},
            options=validated_data,
        )

    @staticmethod
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> OptionsFlowHandler:
        """Get options flow handler."""
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlowWithConfigEntry):
    """Handle options flow."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle options flow."""
        if user_input is None:
            _LOGGER.debug("Showing options form for entry: %s", self.config_entry.entry_id)
            return self.async_show_form(
                step_id="init",
                data_schema=_create_schema(self.hass, self.config_entry.options, flow="options"),
            )
        
        _LOGGER.debug("Options input received: %s", {k: v for k, v in user_input.items() if k != "key"})
        
        error, validated_data = await _validate_input(self.hass, user_input)
        
        if error:
            _LOGGER.warning("Validation error: %s", error)
            return self.async_show_form(
                step_id="init",
                data_schema=_create_schema(self.hass, user_input, flow="options"),
                errors={"base": error},
            )
        
        _LOGGER.info("Updating options for entry %s", self.config_entry.entry_id)
        return self.async_create_entry(title="", data=validated_data)
