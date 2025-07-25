"""Support for APCUPSd sensors."""

from __future__ import annotations

import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    PERCENTAGE,
    EntityCategory,
    UnitOfApparentPower,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfFrequency,
    UnitOfPower,
    UnitOfTemperature,
    UnitOfTime,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import LAST_S_TEST
from .coordinator import APCUPSdConfigEntry, APCUPSdCoordinator

PARALLEL_UPDATES = 0

_LOGGER = logging.getLogger(__name__)

SENSORS: dict[str, SensorEntityDescription] = {
    "alarmdel": SensorEntityDescription(
        key="alarmdel",
        translation_key="alarm_delay",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    "ambtemp": SensorEntityDescription(
        key="ambtemp",
        translation_key="ambient_temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "apc": SensorEntityDescription(
        key="apc",
        translation_key="apc_status",
        entity_registry_enabled_default=False,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    "apcmodel": SensorEntityDescription(
        key="apcmodel",
        translation_key="apc_model",
        entity_registry_enabled_default=False,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    "badbatts": SensorEntityDescription(
        key="badbatts",
        translation_key="bad_batteries",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    "battdate": SensorEntityDescription(
        key="battdate",
        translation_key="battery_replacement_date",
    ),
    "battstat": SensorEntityDescription(
        key="battstat",
        translation_key="battery_status",
    ),
    "battv": SensorEntityDescription(
        key="battv",
        translation_key="battery_voltage",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "bcharge": SensorEntityDescription(
        key="bcharge",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.BATTERY,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "cable": SensorEntityDescription(
        key="cable",
        translation_key="cable_type",
        entity_registry_enabled_default=False,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    "cumonbatt": SensorEntityDescription(
        key="cumonbatt",
        translation_key="total_time_on_battery",
        native_unit_of_measurement=UnitOfTime.SECONDS,
        state_class=SensorStateClass.TOTAL_INCREASING,
        device_class=SensorDeviceClass.DURATION,
    ),
    "date": SensorEntityDescription(
        key="date",
        translation_key="date",
        entity_registry_enabled_default=False,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    "dipsw": SensorEntityDescription(
        key="dipsw",
        translation_key="dip_switch_settings",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    "dlowbatt": SensorEntityDescription(
        key="dlowbatt",
        translation_key="low_battery_signal",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    "driver": SensorEntityDescription(
        key="driver",
        translation_key="driver",
        entity_registry_enabled_default=False,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    "dshutd": SensorEntityDescription(
        key="dshutd",
        translation_key="shutdown_delay",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    "dwake": SensorEntityDescription(
        key="dwake",
        translation_key="wake_delay",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    "end apc": SensorEntityDescription(
        key="end apc",
        translation_key="date_and_time",
        entity_registry_enabled_default=False,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    "extbatts": SensorEntityDescription(
        key="extbatts",
        translation_key="external_batteries",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    "firmware": SensorEntityDescription(
        key="firmware",
        translation_key="firmware_version",
        entity_registry_enabled_default=False,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    "hitrans": SensorEntityDescription(
        key="hitrans",
        translation_key="transfer_high",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    "hostname": SensorEntityDescription(
        key="hostname",
        translation_key="hostname",
        entity_registry_enabled_default=False,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    "humidity": SensorEntityDescription(
        key="humidity",
        translation_key="humidity",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.HUMIDITY,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "itemp": SensorEntityDescription(
        key="itemp",
        translation_key="internal_temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    LAST_S_TEST: SensorEntityDescription(
        key=LAST_S_TEST,
        translation_key="last_self_test",
    ),
    "lastxfer": SensorEntityDescription(
        key="lastxfer",
        translation_key="last_transfer",
        entity_registry_enabled_default=False,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    "linefail": SensorEntityDescription(
        key="linefail",
        translation_key="line_failure",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    "linefreq": SensorEntityDescription(
        key="linefreq",
        translation_key="line_frequency",
        native_unit_of_measurement=UnitOfFrequency.HERTZ,
        device_class=SensorDeviceClass.FREQUENCY,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "linev": SensorEntityDescription(
        key="linev",
        translation_key="line_voltage",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "loadpct": SensorEntityDescription(
        key="loadpct",
        translation_key="load_capacity",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "loadapnt": SensorEntityDescription(
        key="loadapnt",
        translation_key="apparent_power",
        native_unit_of_measurement=PERCENTAGE,
    ),
    "lotrans": SensorEntityDescription(
        key="lotrans",
        translation_key="transfer_low",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    "mandate": SensorEntityDescription(
        key="mandate",
        translation_key="manufacture_date",
        entity_registry_enabled_default=False,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    "masterupd": SensorEntityDescription(
        key="masterupd",
        translation_key="master_update",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    "maxlinev": SensorEntityDescription(
        key="maxlinev",
        translation_key="input_voltage_high",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
    ),
    "maxtime": SensorEntityDescription(
        key="maxtime",
        translation_key="max_time",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    "mbattchg": SensorEntityDescription(
        key="mbattchg",
        translation_key="max_battery_charge",
        native_unit_of_measurement=PERCENTAGE,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    "minlinev": SensorEntityDescription(
        key="minlinev",
        translation_key="input_voltage_low",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
    ),
    "mintimel": SensorEntityDescription(
        key="mintimel",
        translation_key="min_time",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    "model": SensorEntityDescription(
        key="model",
        translation_key="model",
        entity_registry_enabled_default=False,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    "nombattv": SensorEntityDescription(
        key="nombattv",
        translation_key="battery_nominal_voltage",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    "nominv": SensorEntityDescription(
        key="nominv",
        translation_key="nominal_input_voltage",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    "nomoutv": SensorEntityDescription(
        key="nomoutv",
        translation_key="nominal_output_voltage",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    "nompower": SensorEntityDescription(
        key="nompower",
        translation_key="nominal_output_power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    "nomapnt": SensorEntityDescription(
        key="nomapnt",
        translation_key="nominal_apparent_power",
        native_unit_of_measurement=UnitOfApparentPower.VOLT_AMPERE,
        device_class=SensorDeviceClass.APPARENT_POWER,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    "numxfers": SensorEntityDescription(
        key="numxfers",
        translation_key="transfer_count",
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    "outcurnt": SensorEntityDescription(
        key="outcurnt",
        translation_key="output_current",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "outputv": SensorEntityDescription(
        key="outputv",
        translation_key="output_voltage",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "reg1": SensorEntityDescription(
        key="reg1",
        translation_key="register_1_fault",
        entity_registry_enabled_default=False,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    "reg2": SensorEntityDescription(
        key="reg2",
        translation_key="register_2_fault",
        entity_registry_enabled_default=False,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    "reg3": SensorEntityDescription(
        key="reg3",
        translation_key="register_3_fault",
        entity_registry_enabled_default=False,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    "retpct": SensorEntityDescription(
        key="retpct",
        translation_key="restore_capacity",
        native_unit_of_measurement=PERCENTAGE,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    "selftest": SensorEntityDescription(
        key="selftest",
        translation_key="self_test_result",
    ),
    "sense": SensorEntityDescription(
        key="sense",
        translation_key="sensitivity",
        entity_registry_enabled_default=False,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    "serialno": SensorEntityDescription(
        key="serialno",
        translation_key="serial_number",
        entity_registry_enabled_default=False,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    "starttime": SensorEntityDescription(
        key="starttime",
        translation_key="startup_time",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    "statflag": SensorEntityDescription(
        key="statflag",
        translation_key="online_status",
        entity_registry_enabled_default=False,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    "status": SensorEntityDescription(
        key="status",
        translation_key="status",
    ),
    "stesti": SensorEntityDescription(
        key="stesti",
        translation_key="self_test_interval",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    "timeleft": SensorEntityDescription(
        key="timeleft",
        translation_key="time_left",
        native_unit_of_measurement=UnitOfTime.MINUTES,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.DURATION,
    ),
    "tonbatt": SensorEntityDescription(
        key="tonbatt",
        translation_key="time_on_battery",
        native_unit_of_measurement=UnitOfTime.SECONDS,
        state_class=SensorStateClass.TOTAL_INCREASING,
        device_class=SensorDeviceClass.DURATION,
    ),
    "upsmode": SensorEntityDescription(
        key="upsmode",
        translation_key="ups_mode",
    ),
    "upsname": SensorEntityDescription(
        key="upsname",
        translation_key="ups_name",
        entity_registry_enabled_default=False,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    "version": SensorEntityDescription(
        key="version",
        translation_key="version",
        entity_registry_enabled_default=False,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    "xoffbat": SensorEntityDescription(
        key="xoffbat",
        translation_key="transfer_from_battery",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    "xoffbatt": SensorEntityDescription(
        key="xoffbatt",
        translation_key="transfer_from_battery",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    "xonbatt": SensorEntityDescription(
        key="xonbatt",
        translation_key="transfer_to_battery",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
}

INFERRED_UNITS = {
    " Minutes": UnitOfTime.MINUTES,
    " Seconds": UnitOfTime.SECONDS,
    " Percent": PERCENTAGE,
    " Volts": UnitOfElectricPotential.VOLT,
    " Ampere": UnitOfElectricCurrent.AMPERE,
    " Amps": UnitOfElectricCurrent.AMPERE,
    " Volt-Ampere": UnitOfApparentPower.VOLT_AMPERE,
    " VA": UnitOfApparentPower.VOLT_AMPERE,
    " Watts": UnitOfPower.WATT,
    " Hz": UnitOfFrequency.HERTZ,
    " C": UnitOfTemperature.CELSIUS,
    # APCUPSd reports data for "itemp" field (eventually represented by UPS Internal
    # Temperature sensor in this integration) with a trailing "Internal", e.g.,
    # "34.6 C Internal". Here we create a fake unit " C Internal" to handle this case.
    " C Internal": UnitOfTemperature.CELSIUS,
    " Percent Load Capacity": PERCENTAGE,
    # "stesti" field (Self Test Interval) field could report a "days" unit, e.g.,
    # "7 days", so here we add support for it.
    " days": UnitOfTime.DAYS,
}


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: APCUPSdConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the APCUPSd sensors from config entries."""
    coordinator = config_entry.runtime_data

    # The resource keys in the data dict collected in the coordinator is in upper-case
    # by default, but we use lower cases throughout this integration.
    available_resources: set[str] = {k.lower() for k, _ in coordinator.data.items()}

    entities = []

    # "laststest" is a special sensor that only appears when the APC UPS daemon has done a
    # periodical (or manual) self test since last daemon restart. It might not be available
    # when we set up the integration, and we do not know if it would ever be available. Here we
    # add it anyway and mark it as unknown initially.
    for resource in available_resources | {LAST_S_TEST}:
        if resource not in SENSORS:
            _LOGGER.warning("Invalid resource from APCUPSd: %s", resource.upper())
            continue

        entities.append(APCUPSdSensor(coordinator, SENSORS[resource]))

    async_add_entities(entities)


def infer_unit(value: str) -> tuple[str, str | None]:
    """If the value ends with any of the units from supported units.

    Split the unit off the end of the value and return the value, unit tuple
    pair. Else return the original value and None as the unit.
    """

    for unit, ha_unit in INFERRED_UNITS.items():
        if value.endswith(unit):
            return value.removesuffix(unit), ha_unit

    return value, None


class APCUPSdSensor(CoordinatorEntity[APCUPSdCoordinator], SensorEntity):
    """Representation of a sensor entity for APCUPSd status values."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: APCUPSdCoordinator,
        description: SensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator=coordinator, context=description.key.upper())

        self.entity_description = description
        self._attr_unique_id = f"{coordinator.unique_device_id}_{description.key}"
        self._attr_device_info = coordinator.device_info

        # Initial update of attributes.
        self._update_attrs()

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._update_attrs()
        self.async_write_ha_state()

    def _update_attrs(self) -> None:
        """Update sensor attributes based on coordinator data."""
        key = self.entity_description.key.upper()
        # For most sensors the key will always be available for each refresh. However, some sensors
        # (e.g., "laststest") will only appear after certain event occurs (e.g., a self test is
        # performed) and may disappear again after certain event. So we mark the state as "unknown"
        # when it becomes unknown after such events.
        if key not in self.coordinator.data:
            self._attr_native_value = None
            return

        self._attr_native_value, inferred_unit = infer_unit(self.coordinator.data[key])
        if not self.native_unit_of_measurement:
            self._attr_native_unit_of_measurement = inferred_unit
