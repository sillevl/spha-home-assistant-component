import asyncio
import logging
from homeassistant.components import mqtt
from homeassistant.components.light import LightEntity

import voluptuous as vol
import homeassistant.helpers.config_validation as cv

TURN_ON_PAYLOAD = "on"
TURN_OFF_PAYLOAD = "off"

_LOGGER = logging.getLogger(__name__)

CONF_PLATFORM = "platform"
CONF_NAME = "name"
CONF_NUMBER = "number"
DEFAULT_NAME = "Teletask Light"

PLATFORM_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_PLATFORM): cv.string,
        vol.Required(CONF_NUMBER): cv.positive_int,
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    }
)


def setup_platform(hass, config, add_entities, discovery_info=None):
    add_entities([TeletaskLight(config, hass.components.mqtt)])


class TeletaskLight(LightEntity):
    def __init__(self, config, mqtt):
        self._mqtt = mqtt
        self._is_on = False
        self._state = None
        self._name = (
            config["name"]
            if config["name"] != DEFAULT_NAME
            else config["name"] + " " + str(config["number"])
        )
        self._number = config["number"]
        # TODO: make first part topic configurable
        self._state_topic = "teletask/relay/{number}".format(number=self._number)
        self._command_topic = "teletask/relay/{number}/set".format(number=self._number)

        def message_received(topic, payload, qos):
            """A new MQTT message has been received."""
            self._state = payload == TURN_ON_PAYLOAD
            self.schedule_update_ha_state()

        self._mqtt.subscribe(self._state_topic, message_received)

    @property
    def name(self):
        """Name of the device."""
        return self._name

    @property
    def unique_id(self):
        # TODO: get first part from domain
        return "teletask_sillevl.light.{number}".format(number=self._number)

    @property
    def is_on(self):
        """Return true if light is on."""
        return self._state

    def turn_off(self, **kwargs):
        """Turn the device off."""
        self._mqtt.publish(self._command_topic, TURN_OFF_PAYLOAD)

    def turn_on(self, **kwargs):
        """Turn the device on."""
        self._mqtt.publish(self._command_topic, TURN_ON_PAYLOAD)
