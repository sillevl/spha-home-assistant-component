"""Exercise cover commands with lightweight HA and timer doubles."""

import ast
import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, Mock

import pytest

from const import COVER_AUTO_STOP_TIMEOUT_SECONDS


@pytest.fixture
def cover():
    # Load the actual entity class without requiring a Home Assistant install.
    source = (Path(__file__).resolve().parents[1] / "cover.py").read_text(
        encoding="utf-8"
    )
    tree = ast.parse(source)
    entity = next(
        node for node in tree.body
        if isinstance(node, ast.ClassDef) and node.name == "SphaCover"
    )
    base = type("CoverEntity", (), {"async_will_remove_from_hass": AsyncMock()})
    schedule = Mock()
    namespace = {
        "CoverEntity": base,
        "async_call_later": schedule,
        "COVER_AUTO_STOP_TIMEOUT_SECONDS": COVER_AUTO_STOP_TIMEOUT_SECONDS,
    }
    exec(compile(ast.Module(body=[entity], type_ignores=[]), "cover.py", "exec"), namespace)
    instance = object.__new__(namespace["SphaCover"])
    instance._hass = object()
    instance._cancel_auto_stop = None
    instance._open_relay = Mock(async_turn_on=AsyncMock(), async_turn_off=AsyncMock())
    instance._close_relay = Mock(async_turn_on=AsyncMock(), async_turn_off=AsyncMock())
    instance.async_write_ha_state = Mock()
    return instance, schedule


@pytest.mark.parametrize("direction", ["open", "close"])
def test_movement_stops_both_relays_after_35_seconds(cover, direction):
    instance, schedule = cover

    async def scenario():
        await getattr(instance, f"async_{direction}_cover")()
        schedule.assert_called_once()
        hass, delay, callback = schedule.call_args.args
        assert hass is instance._hass
        assert delay == COVER_AUTO_STOP_TIMEOUT_SECONDS == 35
        assert instance._attr_is_opening == (direction == "open")
        assert instance._attr_is_closing == (direction == "close")
        instance._open_relay.async_turn_off.reset_mock()
        instance._close_relay.async_turn_off.reset_mock()

        await callback(None)

        instance._open_relay.async_turn_off.assert_awaited_once()
        instance._close_relay.async_turn_off.assert_awaited_once()
        assert not instance._attr_is_opening
        assert not instance._attr_is_closing
        assert instance._cancel_auto_stop is None
        assert instance.async_write_ha_state.call_count == 2

    asyncio.run(scenario())


@pytest.mark.parametrize("next_command", ["open", "close", "stop"])
def test_new_command_cancels_previous_timer(cover, next_command):
    instance, schedule = cover

    async def scenario():
        await instance.async_open_cover()
        cancel = schedule.return_value
        await getattr(instance, f"async_{next_command}_cover")()
        cancel.assert_called_once_with()
        assert schedule.call_count == (1 if next_command == "stop" else 2)
        if next_command == "stop":
            assert instance._cancel_auto_stop is None

    asyncio.run(scenario())


def test_removal_cancels_timer(cover):
    instance, schedule = cover

    async def scenario():
        await instance.async_open_cover()
        await instance.async_will_remove_from_hass()
        schedule.return_value.assert_called_once_with()
        assert instance._cancel_auto_stop is None

    asyncio.run(scenario())


@pytest.mark.parametrize("direction", ["open", "close"])
def test_opposite_relay_is_disabled_before_enabling_direction(cover, direction):
    instance, _ = cover
    calls = Mock()
    opposite = "close" if direction == "open" else "open"
    calls.attach_mock(getattr(instance, f"_{opposite}_relay").async_turn_off, "off")
    calls.attach_mock(getattr(instance, f"_{direction}_relay").async_turn_on, "on")

    asyncio.run(getattr(instance, f"async_{direction}_cover")())

    assert [call[0] for call in calls.mock_calls] == ["off", "on"]
