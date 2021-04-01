import asyncio
import logging
from homeassistant.components.light import LightEntity


_LOGGER = logging.getLogger(__name__)

# breakpoint()


async def async_setup_platform(hass, config, add_entities, discovery_info=None):
    add_entities([TeletaskLight(config)])


class TeletaskLight(LightEntity):
    def __init__(self, config):
        print("**********************")
        print(config)
        self._is_on = False
        self._state = None
        self._name = config["name"]
        self._number = config["number"]

    @property
    def name(self):
        """Name of the device."""
        return self._name

    @property
    def unique_id(self):
        return "teletask_sillevl.light.{number}".format(number=self._number)

    @property
    def is_on(self):
        """Return true if light is on."""
        return self._state

    def turn_off(self, **kwargs):
        """Turn the device off."""

    async def async_turn_off(self, **kwargs):
        """Turn device off."""

    def turn_on(self, **kwargs):
        """Turn the device on."""

    async def async_turn_on(self, **kwargs):
        """Turn device on."""