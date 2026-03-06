import pytest

from utils import cover_channel_relays, parse_relay_state_payload


@pytest.mark.parametrize(
    ("payload", "expected"),
    [
        ("on", True),
        ("off", False),
        (" ON ", True),
        ("OFF", False),
        ('{"state":"on"}', True),
        ('{"state":"off"}', False),
        ('{"state":"ON"}', True),
        (b'{"state":"off"}', False),
    ],
)
def test_parse_relay_state_payload_valid(payload, expected):
    assert parse_relay_state_payload(payload) is expected


@pytest.mark.parametrize(
    "payload",
    [
        None,
        "",
        "unknown",
        "{",
        "[]",
        "{}",
        '{"state": 1}',
        '{"state": "toggle"}',
        b"\xff\xfe",
    ],
)
def test_parse_relay_state_payload_invalid(payload):
    assert parse_relay_state_payload(payload) is None


@pytest.mark.parametrize(
    ("channel", "expected_close", "expected_open"),
    [
        (1, 0, 1),
        (2, 2, 3),
        (4, 6, 7),
    ],
)
def test_cover_channel_relays(channel, expected_close, expected_open):
    close_relay, open_relay = cover_channel_relays(channel)
    assert close_relay == expected_close
    assert open_relay == expected_open


@pytest.mark.parametrize("channel", [0, -1, 1.5, "1", None])
def test_cover_channel_relays_invalid(channel):
    with pytest.raises(ValueError):
        cover_channel_relays(channel)
