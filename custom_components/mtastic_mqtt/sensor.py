"""Sensor platform for Meshtastic MQTT integration."""
from __future__ import annotations

from typing import Any
from homeassistant.components import sensor
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import EntityCategory

from .coordinator import BaseEntity, Coordinator
from .constants import DOMAIN

import logging

_LOGGER = logging.getLogger(__name__)



async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensors from a config entry."""
    coordinator: Coordinator = entry.runtime_data
    
    entities = [
        LastUpdateSensor(coordinator),
        TelemetryBatterySensor(coordinator),
        TelemetryVoltageSensor(coordinator),
        TelemetryAirtimeUtilSensor(coordinator),
        TelemetryChannelUtilSensor(coordinator),
        NeighborsSensor(coordinator),
        TelemetryTemperatureSensor(coordinator),
        TelemetryRelativeHumiditySensor(coordinator),
        TelemetryBarometricPressureSensor(coordinator),
        TelemetryGasResistanceSensor(coordinator),
        _TelemetryRadiation(coordinator),
        _TelemetryCh1Voltage(coordinator),
        _TelemetryCh1Current(coordinator),
        _TelemetryCh2Voltage(coordinator),
        _TelemetryCh2Current(coordinator),
        _TelemetryCh3Voltage(coordinator),
        _TelemetryCh3Current(coordinator),
        _TelemetryCh4Voltage(coordinator),
        _TelemetryCh4Current(coordinator),
        _TelemetryCh5Voltage(coordinator),
        _TelemetryCh5Current(coordinator),
        _TelemetryCh6Voltage(coordinator),
        _TelemetryCh6Current(coordinator),
        _TelemetryCh7Voltage(coordinator),
        _TelemetryCh7Current(coordinator),
        _TelemetryCh8Voltage(coordinator),
        _TelemetryCh8Current(coordinator),
    ]

    async_add_entities(entities)
    _LOGGER.debug("Added %d sensor entities", len(entities))


class LastUpdateSensor(BaseEntity, sensor.SensorEntity):
    """Sensor for last update timestamp."""

    def __init__(self, coordinator: Coordinator) -> None:
        """Initialize sensor."""
        super().__init__(coordinator)
        self.with_name("last_update", "Last Update")
        self._attr_entity_category = EntityCategory.DIAGNOSTIC
        self._attr_device_class = sensor.SensorDeviceClass.TIMESTAMP

    @property
    def native_value(self) -> Any:
        """Return the state of the sensor."""
        return self.coordinator.last_update

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        result: dict[str, Any] = {}
        if nodeinfo := self.coordinator.data.get("nodeinfo"):
            for attr in ("id", "longname", "shortname"):
                if value := nodeinfo.get(attr):
                    result[attr] = value
        return result


class TelemetryBatterySensor(BaseEntity, sensor.SensorEntity):
    """Sensor for battery level."""

    def __init__(self, coordinator: Coordinator) -> None:
        """Initialize sensor."""
        super().__init__(coordinator)
        self.with_name("tel_battery_level", "Battery")
        self._attr_device_class = sensor.SensorDeviceClass.BATTERY
        self._attr_state_class = sensor.SensorStateClass.MEASUREMENT
        self._attr_native_unit_of_measurement = "%"
        self._attr_entity_registry_enabled_default = False
        self._attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        if tel := self.coordinator.data.get("device_metrics"):
            if (value := tel.get("battery_level", 0)) > 0:
                return min(100.0, float(value))
        return None


class TelemetryVoltageSensor(BaseEntity, sensor.SensorEntity):
    """Sensor for voltage."""

    def __init__(self, coordinator: Coordinator) -> None:
        """Initialize sensor."""
        super().__init__(coordinator)
        self.with_name("tel_voltage", "Voltage")
        self._attr_device_class = sensor.SensorDeviceClass.VOLTAGE
        self._attr_state_class = sensor.SensorStateClass.MEASUREMENT
        self._attr_native_unit_of_measurement = "V"
        self._attr_suggested_display_precision = 2
        self._attr_entity_registry_enabled_default = False
        self._attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        if tel := self.coordinator.data.get("device_metrics"):
            if (value := tel.get("voltage", 0)) > 0:
                return float(value)
        return None


class TelemetryAirtimeUtilSensor(BaseEntity, sensor.SensorEntity):
    """Sensor for TX airtime utilization."""

    def __init__(self, coordinator: Coordinator) -> None:
        """Initialize sensor."""
        super().__init__(coordinator)
        self.with_name("tel_air_util_tx", "Tx Airtime Utilization")
        self._attr_state_class = sensor.SensorStateClass.MEASUREMENT
        self._attr_native_unit_of_measurement = "%"
        self._attr_suggested_display_precision = 1
        self._attr_entity_registry_enabled_default = False
        self._attr_icon = "mdi:cloud-percent"
        self._attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        if tel := self.coordinator.data.get("device_metrics"):
            if value := tel.get("air_util_tx"):
                return float(value)
        return None


class TelemetryChannelUtilSensor(BaseEntity, sensor.SensorEntity):
    """Sensor for channel utilization."""

    def __init__(self, coordinator: Coordinator) -> None:
        """Initialize sensor."""
        super().__init__(coordinator)
        self.with_name("tel_channel_utilization", "Channel Utilization")
        self._attr_state_class = sensor.SensorStateClass.MEASUREMENT
        self._attr_native_unit_of_measurement = "%"
        self._attr_suggested_display_precision = 1
        self._attr_entity_registry_enabled_default = False
        self._attr_icon = "mdi:gauge"
        self._attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        if tel := self.coordinator.data.get("device_metrics"):
            if value := tel.get("channel_utilization"):
                return float(value)
        return None


class NeighborsSensor(BaseEntity, sensor.SensorEntity):
    """Sensor for neighbors count."""

    def __init__(self, coordinator: Coordinator) -> None:
        """Initialize sensor."""
        super().__init__(coordinator)
        self.with_name("nn_neighbors", "Neighbors Count")
        self._attr_state_class = sensor.SensorStateClass.MEASUREMENT
        self._attr_suggested_display_precision = 0
        self._attr_entity_registry_enabled_default = False
        self._attr_icon = "mdi:map-marker-multiple-outline"
        self._attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def native_value(self) -> int | None:
        """Return the state of the sensor."""
        if nn := self.coordinator.data.get("neighborinfo"):
            if (value := nn.get("neighbors_count", -1)) >= 0:
                return int(value)
        return None


class TelemetryTemperatureSensor(BaseEntity, sensor.SensorEntity):
    """Sensor for temperature."""

    def __init__(self, coordinator: Coordinator) -> None:
        """Initialize sensor."""
        super().__init__(coordinator)
        self.with_name("tel_temperature", "Temperature")
        self._attr_device_class = sensor.SensorDeviceClass.TEMPERATURE
        self._attr_state_class = sensor.SensorStateClass.MEASUREMENT
        self._attr_native_unit_of_measurement = "°C"
        self._attr_suggested_display_precision = 1
        self._attr_entity_registry_enabled_default = False

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        if tel := self.coordinator.data.get("environment_metrics"):
            if (value := tel.get("temperature", 0)) > 0:
                return float(value)
        return None


class TelemetryRelativeHumiditySensor(BaseEntity, sensor.SensorEntity):
    """Sensor for relative humidity."""

    def __init__(self, coordinator: Coordinator) -> None:
        """Initialize sensor."""
        super().__init__(coordinator)
        self.with_name("tel_relativehumidity", "Relative Humidity")
        self._attr_device_class = sensor.SensorDeviceClass.HUMIDITY
        self._attr_state_class = sensor.SensorStateClass.MEASUREMENT
        self._attr_native_unit_of_measurement = "%"
        self._attr_suggested_display_precision = 1
        self._attr_entity_registry_enabled_default = False

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        if tel := self.coordinator.data.get("environment_metrics"):
            if (value := tel.get("relative_humidity", 0)) > 0:
                return float(value)
        return None


class TelemetryBarometricPressureSensor(BaseEntity, sensor.SensorEntity):
    """Sensor for barometric pressure."""

    def __init__(self, coordinator: Coordinator) -> None:
        """Initialize sensor."""
        super().__init__(coordinator)
        self.with_name("tel_barometric_pressure", "Barometric Pressure")
        self._attr_device_class = sensor.SensorDeviceClass.ATMOSPHERIC_PRESSURE
        self._attr_state_class = sensor.SensorStateClass.MEASUREMENT
        self._attr_native_unit_of_measurement = "hPa"
        self._attr_suggested_display_precision = 1
        self._attr_entity_registry_enabled_default = False

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        if tel := self.coordinator.data.get("environment_metrics"):
            if (value := tel.get("barometric_pressure", 0)) > 0:
                return float(value)
        return None


class TelemetryGasResistanceSensor(BaseEntity, sensor.SensorEntity):
    """Sensor for gas resistance (AQI)."""

    def __init__(self, coordinator: Coordinator) -> None:
        """Initialize sensor."""
        super().__init__(coordinator)
        self.with_name("tel_gas_resistance", "Gas Resistance (AQI)")
        self._attr_device_class = sensor.SensorDeviceClass.AQI
        self._attr_state_class = sensor.SensorStateClass.MEASUREMENT
        self._attr_suggested_display_precision = 1
        self._attr_entity_registry_enabled_default = False

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        if tel := self.coordinator.data.get("environment_metrics"):
            if (value := tel.get("gas_resistance", 0)) > 0:
                return float(value)
        return None

class _TelemetryRadiation(BaseEntity, sensor.SensorEntity):

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self.with_name(f"tel_radiation", "Radiation")
        self._attr_state_class = sensor.SensorStateClass.MEASUREMENT        self._attr_native_unit_of_measurement = "µR/h"
        self._attr_suggested_display_precision = 1
        self._attr_entity_registry_enabled_default = False
        self._attr_icon = "mdi:radioactive"


    @property
    def native_value(self) -> float | None:
        if tel := self.coordinator.data.get("environment_metrics"):
            if (value := tel.get("radiation")) > 0:
                return value
        return None

class _TelemetryCh1Voltage(BaseEntity, sensor.SensorEntity):

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self.with_name(f"tel_ch1_voltage", "Voltage 1")
        self._attr_device_class = sensor.SensorDeviceClass.VOLTAGE
        self._attr_state_class = sensor.SensorStateClass.MEASUREMENT
        self._attr_native_unit_of_measurement = "V"
        self._attr_suggested_display_precision = 2
        self._attr_entity_registry_enabled_default = False
        self._attr_icon = "mdi:flash-outline"


    @property
    def native_value(self) -> float | None:
        if tel := self.coordinator.data.get("power_metrics"):
            if (value := tel.get("ch1_voltage")) > 0:
                return value
        return None
    
class _TelemetryCh1Current(BaseEntity, sensor.SensorEntity):

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self.with_name(f"tel_ch1_current", "Current 1")
        self._attr_device_class = sensor.SensorDeviceClass.CURRENT
        self._attr_state_class = sensor.SensorStateClass.MEASUREMENT
        self._attr_native_unit_of_measurement = "mA"
        self._attr_suggested_display_precision = 1
        self._attr_entity_registry_enabled_default = False
        self._attr_icon = "mdi:current-dc"


    @property
    def native_value(self) -> float | None:
        if tel := self.coordinator.data.get("power_metrics"):
            if (value := tel.get("ch1_current")) > 0:
                return value
        return None
    
class _TelemetryCh2Voltage(BaseEntity, sensor.SensorEntity):

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self.with_name(f"tel_ch2_voltage", "Voltage 2")
        self._attr_device_class = sensor.SensorDeviceClass.VOLTAGE
        self._attr_state_class = sensor.SensorStateClass.MEASUREMENT
        self._attr_native_unit_of_measurement = "V"
        self._attr_suggested_display_precision = 2
        self._attr_entity_registry_enabled_default = False
        self._attr_icon = "mdi:flash-outline"


    @property
    def native_value(self) -> float | None:
        if tel := self.coordinator.data.get("power_metrics"):
            if (value := tel.get("ch2_voltage")) > 0:
                return value
        return None
    
class _TelemetryCh2Current(BaseEntity, sensor.SensorEntity):

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self.with_name(f"tel_ch2_current", "Current 2")
        self._attr_device_class = sensor.SensorDeviceClass.CURRENT
        self._attr_state_class = sensor.SensorStateClass.MEASUREMENT
        self._attr_native_unit_of_measurement = "mA"
        self._attr_suggested_display_precision = 1
        self._attr_entity_registry_enabled_default = False
        self._attr_icon = "mdi:current-dc"


    @property
    def native_value(self) -> float | None:
        if tel := self.coordinator.data.get("power_metrics"):
            if (value := tel.get("ch2_current")) > 0:
                return value
        return None
    
class _TelemetryCh3Voltage(BaseEntity, sensor.SensorEntity):

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self.with_name(f"tel_ch3_voltage", "Voltage 3")
        self._attr_device_class = sensor.SensorDeviceClass.VOLTAGE
        self._attr_state_class = sensor.SensorStateClass.MEASUREMENT
        self._attr_native_unit_of_measurement = "V"
        self._attr_suggested_display_precision = 2
        self._attr_entity_registry_enabled_default = False
        self._attr_icon = "mdi:flash-outline"


    @property
    def native_value(self) -> float | None:
        if tel := self.coordinator.data.get("power_metrics"):
            if (value := tel.get("ch3_voltage")) > 0:
                return value
        return None
    
class _TelemetryCh3Current(BaseEntity, sensor.SensorEntity):

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self.with_name(f"tel_ch3_current", "Current 3")
        self._attr_device_class = sensor.SensorDeviceClass.CURRENT
        self._attr_state_class = sensor.SensorStateClass.MEASUREMENT
        self._attr_native_unit_of_measurement = "mA"
        self._attr_suggested_display_precision = 1
        self._attr_entity_registry_enabled_default = False
        self._attr_icon = "mdi:current-dc"


    @property
    def native_value(self) -> float | None:
        if tel := self.coordinator.data.get("power_metrics"):
            if (value := tel.get("ch3_current")) > 0:
                return value
        return None
    
class _TelemetryCh4Voltage(BaseEntity, sensor.SensorEntity):

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self.with_name(f"tel_ch4_voltage", "Voltage 4")
        self._attr_device_class = sensor.SensorDeviceClass.VOLTAGE
        self._attr_state_class = sensor.SensorStateClass.MEASUREMENT
        self._attr_native_unit_of_measurement = "V"
        self._attr_suggested_display_precision = 2
        self._attr_entity_registry_enabled_default = False
        self._attr_icon = "mdi:flash-outline"


    @property
    def native_value(self) -> float | None:
        if tel := self.coordinator.data.get("power_metrics"):
            if (value := tel.get("ch4_voltage")) > 0:
                return value
        return None
    
class _TelemetryCh4Current(BaseEntity, sensor.SensorEntity):

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self.with_name(f"tel_ch4_current", "Current 4")
        self._attr_device_class = sensor.SensorDeviceClass.CURRENT
        self._attr_state_class = sensor.SensorStateClass.MEASUREMENT
        self._attr_native_unit_of_measurement = "mA"
        self._attr_suggested_display_precision = 1
        self._attr_entity_registry_enabled_default = False
        self._attr_icon = "mdi:current-dc"


    @property
    def native_value(self) -> float | None:
        if tel := self.coordinator.data.get("power_metrics"):
            if (value := tel.get("ch4_current")) > 0:
                return value
        return None

class _TelemetryCh5Voltage(BaseEntity, sensor.SensorEntity):

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self.with_name(f"tel_ch5_voltage", "Voltage 5")
        self._attr_device_class = sensor.SensorDeviceClass.VOLTAGE
        self._attr_state_class = sensor.SensorStateClass.MEASUREMENT
        self._attr_native_unit_of_measurement = "V"
        self._attr_suggested_display_precision = 2
        self._attr_entity_registry_enabled_default = False
        self._attr_icon = "mdi:flash-outline"


    @property
    def native_value(self) -> float | None:
        if tel := self.coordinator.data.get("power_metrics"):
            if (value := tel.get("ch5_voltage")) > 0:
                return value
        return None
    
class _TelemetryCh5Current(BaseEntity, sensor.SensorEntity):

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self.with_name(f"tel_ch5_current", "Current 5")
        self._attr_device_class = sensor.SensorDeviceClass.CURRENT
        self._attr_state_class = sensor.SensorStateClass.MEASUREMENT
        self._attr_native_unit_of_measurement = "mA"
        self._attr_suggested_display_precision = 1
        self._attr_entity_registry_enabled_default = False
        self._attr_icon = "mdi:current-dc"


    @property
    def native_value(self) -> float | None:
        if tel := self.coordinator.data.get("power_metrics"):
            if (value := tel.get("ch5_current")) > 0:
                return value
        return None
    
class _TelemetryCh6Voltage(BaseEntity, sensor.SensorEntity):

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self.with_name(f"tel_ch6_voltage", "Voltage 6")
        self._attr_device_class = sensor.SensorDeviceClass.VOLTAGE
        self._attr_state_class = sensor.SensorStateClass.MEASUREMENT
        self._attr_native_unit_of_measurement = "V"
        self._attr_suggested_display_precision = 2
        self._attr_entity_registry_enabled_default = False
        self._attr_icon = "mdi:flash-outline"


    @property
    def native_value(self) -> float | None:
        if tel := self.coordinator.data.get("power_metrics"):
            if (value := tel.get("ch6_voltage")) > 0:
                return value
        return None
    
class _TelemetryCh6Current(BaseEntity, sensor.SensorEntity):

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self.with_name(f"tel_ch6_current", "Current 6")
        self._attr_device_class = sensor.SensorDeviceClass.CURRENT
        self._attr_state_class = sensor.SensorStateClass.MEASUREMENT
        self._attr_native_unit_of_measurement = "mA"
        self._attr_suggested_display_precision = 1
        self._attr_entity_registry_enabled_default = False
        self._attr_icon = "mdi:current-dc"


    @property
    def native_value(self) -> float | None:
        if tel := self.coordinator.data.get("power_metrics"):
            if (value := tel.get("ch6_current")) > 0:
                return value
        return None
    
class _TelemetryCh7Voltage(BaseEntity, sensor.SensorEntity):

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self.with_name(f"tel_ch7_voltage", "Voltage 7")
        self._attr_device_class = sensor.SensorDeviceClass.VOLTAGE
        self._attr_state_class = sensor.SensorStateClass.MEASUREMENT
        self._attr_native_unit_of_measurement = "V"
        self._attr_suggested_display_precision = 2
        self._attr_entity_registry_enabled_default = False
        self._attr_icon = "mdi:flash-outline"


    @property
    def native_value(self) -> float | None:
        if tel := self.coordinator.data.get("power_metrics"):
            if (value := tel.get("ch7_voltage")) > 0:
                return value
        return None
    
class _TelemetryCh7Current(BaseEntity, sensor.SensorEntity):

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self.with_name(f"tel_ch7_current", "Current 7")
        self._attr_device_class = sensor.SensorDeviceClass.CURRENT
        self._attr_state_class = sensor.SensorStateClass.MEASUREMENT
        self._attr_native_unit_of_measurement = "mA"
        self._attr_suggested_display_precision = 1
        self._attr_entity_registry_enabled_default = False
        self._attr_icon = "mdi:current-dc"


    @property
    def native_value(self) -> float | None:
        if tel := self.coordinator.data.get("power_metrics"):
            if (value := tel.get("ch7_current")) > 0:
                return value
        return None
    
class _TelemetryCh8Voltage(BaseEntity, sensor.SensorEntity):

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self.with_name(f"tel_ch8_voltage", "Voltage 8")
        self._attr_device_class = sensor.SensorDeviceClass.VOLTAGE
        self._attr_state_class = sensor.SensorStateClass.MEASUREMENT
        self._attr_native_unit_of_measurement = "V"
        self._attr_suggested_display_precision = 2
        self._attr_entity_registry_enabled_default = False
        self._attr_icon = "mdi:flash-outline"


    @property
    def native_value(self) -> float | None:
        if tel := self.coordinator.data.get("power_metrics"):
            if (value := tel.get("ch8_voltage")) > 0:
                return value
        return None
    
class _TelemetryCh8Current(BaseEntity, sensor.SensorEntity):

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self.with_name(f"tel_ch8_current", "Current 8")
        self._attr_device_class = sensor.SensorDeviceClass.CURRENT
        self._attr_state_class = sensor.SensorStateClass.MEASUREMENT
        self._attr_native_unit_of_measurement = "mA"
        self._attr_suggested_display_precision = 1
        self._attr_entity_registry_enabled_default = False
        self._attr_icon = "mdi:current-dc"


    @property
    def native_value(self) -> float | None:
        if tel := self.coordinator.data.get("power_metrics"):
            if (value := tel.get("ch8_current")) > 0:
                return value
        return None
