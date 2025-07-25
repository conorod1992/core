"""The Synology DSM component."""

from __future__ import annotations

from itertools import chain
import logging

from synology_dsm.api.surveillance_station import SynoSurveillanceStation
from synology_dsm.api.surveillance_station.camera import SynoCamera
from synology_dsm.exceptions import SynologyDSMNotLoggedInException

from homeassistant.const import CONF_MAC, CONF_SCAN_INTERVAL, CONF_VERIFY_SSL
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import config_validation as cv, device_registry as dr
from homeassistant.helpers.typing import ConfigType

from .common import SynoApi, raise_config_entry_auth_error
from .const import (
    CONF_BACKUP_PATH,
    CONF_BACKUP_SHARE,
    DATA_BACKUP_AGENT_LISTENERS,
    DEFAULT_VERIFY_SSL,
    DOMAIN,
    EXCEPTION_DETAILS,
    EXCEPTION_UNKNOWN,
    PLATFORMS,
    SYNOLOGY_AUTH_FAILED_EXCEPTIONS,
    SYNOLOGY_CONNECTION_EXCEPTIONS,
)
from .coordinator import (
    SynologyDSMCameraUpdateCoordinator,
    SynologyDSMCentralUpdateCoordinator,
    SynologyDSMConfigEntry,
    SynologyDSMData,
    SynologyDSMSwitchUpdateCoordinator,
)
from .services import async_setup_services

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Synology DSM component."""

    async_setup_services(hass)

    return True


async def async_setup_entry(hass: HomeAssistant, entry: SynologyDSMConfigEntry) -> bool:
    """Set up Synology DSM sensors."""

    # Migrate device identifiers
    dev_reg = dr.async_get(hass)
    devices: list[dr.DeviceEntry] = dr.async_entries_for_config_entry(
        dev_reg, entry.entry_id
    )
    for device in devices:
        old_identifier = list(next(iter(device.identifiers)))
        if len(old_identifier) > 2:
            new_identifier = {
                (old_identifier.pop(0), "_".join([str(x) for x in old_identifier]))
            }
            _LOGGER.debug(
                "migrate identifier '%s' to '%s'", device.identifiers, new_identifier
            )
            dev_reg.async_update_device(device.id, new_identifiers=new_identifier)

    # Migrate existing entry configuration
    if entry.data.get(CONF_VERIFY_SSL) is None:
        hass.config_entries.async_update_entry(
            entry, data={**entry.data, CONF_VERIFY_SSL: DEFAULT_VERIFY_SSL}
        )
    if CONF_BACKUP_SHARE not in entry.options:
        hass.config_entries.async_update_entry(
            entry,
            options={**entry.options, CONF_BACKUP_SHARE: None, CONF_BACKUP_PATH: None},
        )
    if CONF_SCAN_INTERVAL in entry.options:
        current_options = {**entry.options}
        current_options.pop(CONF_SCAN_INTERVAL)
        hass.config_entries.async_update_entry(entry, options=current_options)

    # Continue setup
    api = SynoApi(hass, entry)
    try:
        await api.async_setup()
    except SYNOLOGY_AUTH_FAILED_EXCEPTIONS as err:
        raise_config_entry_auth_error(err)
    except (*SYNOLOGY_CONNECTION_EXCEPTIONS, SynologyDSMNotLoggedInException) as err:
        # SynologyDSMNotLoggedInException may be raised even if the user is
        # logged in because the session may have expired, and we need to retry
        # the login later.
        if err.args[0] and isinstance(err.args[0], dict):
            details = err.args[0].get(EXCEPTION_DETAILS, EXCEPTION_UNKNOWN)
        else:
            details = EXCEPTION_UNKNOWN
        raise ConfigEntryNotReady(details) from err

    # For SSDP compat
    if not entry.data.get(CONF_MAC):
        hass.config_entries.async_update_entry(
            entry, data={**entry.data, CONF_MAC: api.dsm.network.macs}
        )

    coordinator_central = SynologyDSMCentralUpdateCoordinator(hass, entry, api)

    available_apis = api.dsm.apis

    coordinator_cameras: SynologyDSMCameraUpdateCoordinator | None = None
    if api.surveillance_station is not None:
        coordinator_cameras = SynologyDSMCameraUpdateCoordinator(hass, entry, api)
        await coordinator_cameras.async_config_entry_first_refresh()

    coordinator_switches: SynologyDSMSwitchUpdateCoordinator | None = None
    if (
        SynoSurveillanceStation.INFO_API_KEY in available_apis
        and SynoSurveillanceStation.HOME_MODE_API_KEY in available_apis
        and api.surveillance_station is not None
    ):
        coordinator_switches = SynologyDSMSwitchUpdateCoordinator(hass, entry, api)
        await coordinator_switches.async_config_entry_first_refresh()
        try:
            await coordinator_switches.async_setup()
        except SYNOLOGY_CONNECTION_EXCEPTIONS as ex:
            raise ConfigEntryNotReady from ex

    entry.runtime_data = SynologyDSMData(
        api=api,
        coordinator_central=coordinator_central,
        coordinator_central_old_update_success=True,
        coordinator_cameras=coordinator_cameras,
        coordinator_switches=coordinator_switches,
    )
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))

    if entry.options[CONF_BACKUP_SHARE]:

        def async_notify_backup_listeners() -> None:
            for listener in hass.data.get(DATA_BACKUP_AGENT_LISTENERS, []):
                listener()

        entry.async_on_unload(
            entry.async_on_state_change(async_notify_backup_listeners)
        )

        def async_check_last_update_success() -> None:
            if (
                last := coordinator_central.last_update_success
            ) is not entry.runtime_data.coordinator_central_old_update_success:
                entry.runtime_data.coordinator_central_old_update_success = last
                async_notify_backup_listeners()

        entry.runtime_data.coordinator_central.async_add_listener(
            async_check_last_update_success
        )

    return True


async def async_unload_entry(
    hass: HomeAssistant, entry: SynologyDSMConfigEntry
) -> bool:
    """Unload Synology DSM sensors."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        entry_data = entry.runtime_data
        await entry_data.api.async_unload()
    return unload_ok


async def _async_update_listener(
    hass: HomeAssistant, entry: SynologyDSMConfigEntry
) -> None:
    """Handle options update."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_remove_config_entry_device(
    hass: HomeAssistant, entry: SynologyDSMConfigEntry, device_entry: dr.DeviceEntry
) -> bool:
    """Remove synology_dsm config entry from a device."""
    data = entry.runtime_data
    api = data.api
    assert api.information is not None
    serial = api.information.serial
    storage = api.storage
    assert storage is not None
    all_cameras: list[SynoCamera] = []
    if api.surveillance_station is not None:
        # get_all_cameras does not do I/O
        all_cameras = api.surveillance_station.get_all_cameras()
    device_ids = chain(
        (camera.id for camera in all_cameras),
        storage.volumes_ids,
        storage.disks_ids,
        storage.volumes_ids,
        (SynoSurveillanceStation.INFO_API_KEY,),  # Camera home/away
    )
    return not device_entry.identifiers.intersection(
        (
            (DOMAIN, serial),  # Base device
            *(
                (DOMAIN, f"{serial}_{device_id}") for device_id in device_ids
            ),  # Storage and cameras
        )
    )
