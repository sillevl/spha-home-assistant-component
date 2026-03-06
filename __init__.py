"""SPHA custom component."""

try:
    from .const import DOMAIN
except ImportError:  # pragma: no cover - fallback for local direct imports
    from const import DOMAIN


async def async_setup(hass, config):
    return True
