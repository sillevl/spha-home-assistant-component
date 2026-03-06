"""Utility helpers for SPHA entity logic."""

from __future__ import annotations

import json


def parse_relay_state_payload(payload: str | bytes | None) -> bool | None:
    """Parse SPHA relay state payloads.

    Supported payload formats:
    - Plain string: "on" / "off"
    - JSON object: {"state": "on"} / {"state": "off"}
    """
    if payload is None:
        return None

    if isinstance(payload, bytes):
        try:
            payload = payload.decode("utf-8")
        except UnicodeDecodeError:
            return None

    if not isinstance(payload, str):
        return None

    payload_text = payload.strip()
    lowered = payload_text.lower()

    if lowered in ("on", "off"):
        return lowered == "on"

    try:
        message = json.loads(payload_text)
    except json.JSONDecodeError:
        return None

    state = message.get("state") if isinstance(message, dict) else None
    if not isinstance(state, str):
        return None

    state = state.lower()
    if state not in ("on", "off"):
        return None

    return state == "on"


def cover_channel_relays(channel: int) -> tuple[int, int]:
    """Map a cover channel number to close/open relay indices."""
    if not isinstance(channel, int) or channel < 1:
        raise ValueError("channel must be a positive integer")

    close_relay = (channel - 1) * 2
    open_relay = close_relay + 1
    return close_relay, open_relay
