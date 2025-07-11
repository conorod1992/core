"""Test diagnostics of LaCrosse View."""

from unittest.mock import patch

from syrupy.assertion import SnapshotAssertion
from syrupy.filters import props

from homeassistant.components.lacrosse_view.const import DOMAIN
from homeassistant.core import HomeAssistant

from . import MOCK_ENTRY_DATA, TEST_SENSOR

from tests.common import MockConfigEntry
from tests.components.diagnostics import get_diagnostics_for_config_entry
from tests.typing import ClientSessionGenerator


async def test_entry_diagnostics(
    hass: HomeAssistant,
    hass_client: ClientSessionGenerator,
    snapshot: SnapshotAssertion,
) -> None:
    """Test config entry diagnostics."""
    config_entry = MockConfigEntry(
        domain=DOMAIN, data=MOCK_ENTRY_DATA, entry_id="lacrosse_view_test_entry_id"
    )
    config_entry.add_to_hass(hass)

    sensor = TEST_SENSOR.model_copy()
    status = sensor.data
    sensor.data = None

    with (
        patch("lacrosse_view.LaCrosse.login", return_value=True),
        patch("lacrosse_view.LaCrosse.get_devices", return_value=[sensor]),
        patch("lacrosse_view.LaCrosse.get_sensor_status", return_value=status),
    ):
        assert await hass.config_entries.async_setup(config_entry.entry_id)
        await hass.async_block_till_done()

    assert await get_diagnostics_for_config_entry(
        hass, hass_client, config_entry
    ) == snapshot(exclude=props("created_at", "modified_at"))
