import asyncio
import logging
import json
from homeassistant.components import mqtt
from homeassistant.components.light import LightEntity
from homeassistant.core import HomeAssistant

import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType

TURN_ON_PAYLOAD = "on"
TURN_OFF_PAYLOAD = "off"

_LOGGER = logging.getLogger(__name__)

CONF_PLATFORM = "platform"
CONF_NAME = "name"
CONF_MODULE_ID = "module_id"
CONF_RELAY = "relay"
DEFAULT_NAME = "SPHA Light"

PLATFORM_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_PLATFORM): cv.string,
        vol.Required(CONF_MODULE_ID): cv.string,
        vol.Required(CONF_RELAY): cv.positive_int,
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    }
)


def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info=None,
) -> None:
    add_entities([SphaLight(config, hass.components.mqtt, hass)])


class SphaLight(LightEntity):
    def __init__(self, config, mqtt, hass):
        self._hass = hass
        self._mqtt = mqtt
        self._is_on = False
        self._state = None
        self._name = (
            config["name"]
            if config["name"] != DEFAULT_NAME
            else config["name"]
            + " "
            + str(config["module_id"] + "." + str(config["relay"]))
        )
        self._module_id = config["module_id"]
        self._relay = config["relay"]
        # TODO: make first part topic configurable

        self._state_topic = "sixpack/event/relay/{module_id}/{relay}".format(
            module_id=self._module_id, relay=self._relay
        )
        self._command_topic = "sixpack/action/relay/{module_id}/{relay}".format(
            module_id=self._module_id, relay=self._relay
        )

    async def async_init(self):
        def message_received(topic, payload, qos):
            """A new MQTT message has been received."""
            message = json.loads(payload)
            self._state = message["state"] == TURN_ON_PAYLOAD
            self.schedule_update_ha_state()

        self._mqtt.async_subscribe(self._state_topic, message_received)

    @property
    def name(self):
        """Name of the device."""
        return self._name

    @property
    def unique_id(self):
        # TODO: get first part from domain
        return "spha.light.{module_id}.{relay}".format(
            module_id=self._module_id, relay=self._relay
        )

    @property
    def is_on(self):
        """Return true if light is on."""
        return self._state

    def turn_off(self, **kwargs):
        """Turn the device off."""
        payload = {"state": TURN_OFF_PAYLOAD}
        self._mqtt.publish(
            hass=self._hass, topic=self._command_topic, payload=json.dumps(payload)
        )

    def turn_on(self, **kwargs):
        """Turn the device on."""
        payload = {"state": TURN_ON_PAYLOAD}
        self._mqtt.publish(
            hass=self._hass, topic=self._command_topic, payload=json.dumps(payload)
        )
