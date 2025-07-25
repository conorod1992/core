"""Support for monitoring juicenet/juicepoint/juicebox based EVSE sensors."""

from __future__ import annotations

from pyjuicenet import Charger

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfPower,
    UnitOfTemperature,
    UnitOfTime,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import DOMAIN, JUICENET_API, JUICENET_COORDINATOR
from .coordinator import JuiceNetCoordinator
from .device import JuiceNetApi
from .entity import JuiceNetEntity

SENSOR_TYPES: tuple[SensorEntityDescription, ...] = (
    SensorEntityDescription(
        key="status",
        name="Charging Status",
    ),
    SensorEntityDescription(
        key="temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="voltage",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
    ),
    SensorEntityDescription(
        key="amps",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="watts",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="charge_time",
        translation_key="charge_time",
        native_unit_of_measurement=UnitOfTime.SECONDS,
        icon="mdi:timer-outline",
    ),
    SensorEntityDescription(
        key="energy_added",
        translation_key="energy_added",
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the JuiceNet Sensors."""
    juicenet_data = hass.data[DOMAIN][config_entry.entry_id]
    api: JuiceNetApi = juicenet_data[JUICENET_API]
    coordinator: JuiceNetCoordinator = juicenet_data[JUICENET_COORDINATOR]

    entities = [
        JuiceNetSensorDevice(device, coordinator, description)
        for device in api.devices
        for description in SENSOR_TYPES
    ]
    async_add_entities(entities)


class JuiceNetSensorDevice(JuiceNetEntity, SensorEntity):
    """Implementation of a JuiceNet sensor."""

    def __init__(
        self,
        device: Charger,
        coordinator: JuiceNetCoordinator,
        description: SensorEntityDescription,
    ) -> None:
        """Initialise the sensor."""
        super().__init__(device, description.key, coordinator)
        self.entity_description = description

    @property
    def icon(self):
        """Return the icon of the sensor."""
        icon = None
        if self.entity_description.key == "status":
            status = self.device.status
            if status == "standby":
                icon = "mdi:power-plug-off"
            elif status == "plugged":
                icon = "mdi:power-plug"
            elif status == "charging":
                icon = "mdi:battery-positive"
        else:
            icon = self.entity_description.icon
        return icon

    @property
    def native_value(self):
        """Return the state."""
        return getattr(self.device, self.entity_description.key, None)
