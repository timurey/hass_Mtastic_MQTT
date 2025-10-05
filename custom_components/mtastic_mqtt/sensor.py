from homeassistant.components import sensor
from homeassistant.helpers.entity import EntityCategory

from .coordinator import BaseEntity
from .constants import DOMAIN

import logging
_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_setup_entities):
    coordinator = entry.runtime_data
    async_setup_entities([
        _LastUpdate(coordinator),
        _TelemetryBattery(coordinator),
        _TelemetryVoltage(coordinator),
        _TelemetryAirtimelUtil(coordinator),
        _TelemetryChannelUtil(coordinator),
        _Neighbors(coordinator),
        _TelemetryTemperature(coordinator),
        _TelemetryRelativeHumidity(coordinator),
        _TelemetryBarometricPressure(coordinator),
        _TelemetryGasResistance(coordinator),
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


    ])

class _TelemetryBattery(BaseEntity, sensor.SensorEntity):

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self.with_name(f"tel_battery_level", "Battery")
        self._attr_device_class = sensor.SensorDeviceClass.BATTERY
        self._attr_state_class = "measurement"
        self._attr_native_unit_of_measurement = "%"
        self._attr_entity_registry_enabled_default = False
        self._attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def native_value(self) -> float | None:
        if tel := self.coordinator.data.get("device_metrics"):
            if (value := tel.get("battery_level")) > 0:
                return 100 if value > 100 else value
        return None

class _TelemetryVoltage(BaseEntity, sensor.SensorEntity):

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self.with_name(f"tel_voltage", "Voltage")
        self._attr_device_class = sensor.SensorDeviceClass.VOLTAGE
        self._attr_state_class = "measurement"
        self._attr_native_unit_of_measurement = "V"
        self._attr_suggested_display_precision = 1
        self._attr_entity_registry_enabled_default = False
        self._attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def native_value(self) -> float | None:
        if tel := self.coordinator.data.get("device_metrics"):
            if (value := tel.get("voltage")) > 0:
                return value
        return None

class _TelemetryAirtimelUtil(BaseEntity, sensor.SensorEntity):

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self.with_name(f"tel_air_util_tx", "Tx Airtime Utilization")
        self._attr_state_class = "measurement"
        self._attr_native_unit_of_measurement = "%"
        self._attr_suggested_display_precision = 1
        self._attr_entity_registry_enabled_default = False
        self._attr_icon = "mdi:cloud-percent"
        self._attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def native_value(self) -> float | None:
        if tel := self.coordinator.data.get("device_metrics"):
            if value := tel.get("air_util_tx"):
                return value
        return None

class _TelemetryChannelUtil(BaseEntity, sensor.SensorEntity):

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self.with_name(f"tel_channel_utilization", "Channel Utilization")
        self._attr_state_class = "measurement"
        self._attr_native_unit_of_measurement = "%"
        self._attr_suggested_display_precision = 1
        self._attr_entity_registry_enabled_default = False
        self._attr_icon = "mdi:gauge"
        self._attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def native_value(self) -> float | None:
        if tel := self.coordinator.data.get("device_metrics"):
            if value := tel.get("channel_utilization"):
                return value
        return None

class _TelemetryChannelUtil(BaseEntity, sensor.SensorEntity):

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self.with_name(f"tel_channel_utilization", "Channel Utilization")
        self._attr_state_class = "measurement"
        self._attr_native_unit_of_measurement = "%"
        self._attr_suggested_display_precision = 1
        self._attr_entity_registry_enabled_default = False
        self._attr_icon = "mdi:gauge"
        self._attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def native_value(self) -> float | None:
        if tel := self.coordinator.data.get("device_metrics"):
            if value := tel.get("channel_utilization"):
                return value
        return None

class _LastUpdate(BaseEntity, sensor.SensorEntity):

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self.with_name(f"last_update", "Last Update")

        self._attr_entity_category = EntityCategory.DIAGNOSTIC
        self._attr_device_class = sensor.SensorDeviceClass.TIMESTAMP

    @property
    def native_value(self):
        return self.coordinator.last_update

    @property
    def extra_state_attributes(self):
        result = dict()
        if pos := self.coordinator.data.get("nodeinfo"):
            for attr in ("id", "longname", "shortname"):
                if value := pos.get(attr):
                    result[attr] = value
        return result

class _Neighbors(BaseEntity, sensor.SensorEntity):

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self.with_name(f"nn_neighbors", "Neighbors Count")
        self._attr_state_class = "measurement"
        self._attr_suggested_display_precision = 0
        self._attr_entity_registry_enabled_default = False
        self._attr_icon = "mdi:map-marker-multiple-outline"
        self._attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def native_value(self) -> float | None:
        if nn := self.coordinator.data.get("neighborinfo"):
            if (value := nn.get("neighbors_count")) >= 0:
                return value
        return None


class _TelemetryTemperature(BaseEntity, sensor.SensorEntity):

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self.with_name(f"tel_temperature", "Temperature")
        self._attr_device_class = sensor.SensorDeviceClass.TEMPERATURE
        self._attr_state_class = "measurement"
        self._attr_native_unit_of_measurement = "°C"
        self._attr_suggested_display_precision = 1
        self._attr_entity_registry_enabled_default = False

    @property
    def native_value(self) -> float | None:
        if tel := self.coordinator.data.get("environment_metrics"):
            if (value := tel.get("temperature")) > 0:
                return value
        return None


class _TelemetryRelativeHumidity(BaseEntity, sensor.SensorEntity):

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self.with_name(f"tel_relativehumidity", "Relative Humidity")
        self._attr_device_class = sensor.SensorDeviceClass.HUMIDITY
        self._attr_state_class = "measurement"
        self._attr_native_unit_of_measurement = "%"
        self._attr_suggested_display_precision = 1
        self._attr_entity_registry_enabled_default = False

    @property
    def native_value(self) -> float | None:
        if tel := self.coordinator.data.get("environment_metrics"):
            if (value := tel.get("relative_humidity")) > 0:
                return value
        return None


class _TelemetryBarometricPressure(BaseEntity, sensor.SensorEntity):

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self.with_name(f"tel_barometric_pressure", "Barometric Pressure")
        self._attr_device_class = sensor.SensorDeviceClass.ATMOSPHERIC_PRESSURE
        self._attr_state_class = "measurement"
        self._attr_native_unit_of_measurement = "hPa"
        self._attr_suggested_display_precision = 1
        self._attr_entity_registry_enabled_default = False

    @property
    def native_value(self) -> float | None:
        if tel := self.coordinator.data.get("environment_metrics"):
            if (value := tel.get("barometric_pressure")) > 0:
                return value
        return None

class _TelemetryGasResistance(BaseEntity, sensor.SensorEntity):

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self.with_name(f"tel_gas_resistance", "Gas Resistance (AQI)")
        self._attr_device_class = sensor.SensorDeviceClass.AQI
        self._attr_state_class = "measurement"
        self._attr_suggested_display_precision = 1
        self._attr_entity_registry_enabled_default = False

    @property
    def native_value(self) -> float | None:
        if tel := self.coordinator.data.get("environment_metrics"):
            if (value := tel.get("gas_resistance")) > 0:
                return value
        return None

class _TelemetryRadiation(BaseEntity, sensor.SensorEntity):

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self.with_name(f"tel_radiation", "Radiation")
        self._attr_state_class = "measurement"
        self._attr_native_unit_of_measurement = "µR/h"
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
        self._attr_state_class = "measurement"
        self._attr_native_unit_of_measurement = "V"
        self._attr_suggested_display_precision = 1
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
        self._attr_state_class = "measurement"
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
        self._attr_state_class = "measurement"
        self._attr_native_unit_of_measurement = "V"
        self._attr_suggested_display_precision = 1
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
        self._attr_state_class = "measurement"
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
        self._attr_state_class = "measurement"
        self._attr_native_unit_of_measurement = "V"
        self._attr_suggested_display_precision = 1
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
        self._attr_state_class = "measurement"
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
        self._attr_state_class = "measurement"
        self._attr_native_unit_of_measurement = "V"
        self._attr_suggested_display_precision = 1
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
        self._attr_state_class = "measurement"
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
        self._attr_state_class = "measurement"
        self._attr_native_unit_of_measurement = "V"
        self._attr_suggested_display_precision = 1
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
        self._attr_state_class = "measurement"
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
        self._attr_state_class = "measurement"
        self._attr_native_unit_of_measurement = "V"
        self._attr_suggested_display_precision = 1
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
        self._attr_state_class = "measurement"
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
        self._attr_state_class = "measurement"
        self._attr_native_unit_of_measurement = "V"
        self._attr_suggested_display_precision = 1
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
        self._attr_state_class = "measurement"
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
        self._attr_state_class = "measurement"
        self._attr_native_unit_of_measurement = "V"
        self._attr_suggested_display_precision = 1
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
        self._attr_state_class = "measurement"
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
