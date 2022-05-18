import asyncio
import logging
import json
from homeassistant.components import mqtt
from homeassistant.components.cover import CoverEntity
from homeassistant.components.switch import SwitchEntity
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
CONF_CHANNEL = "channel"
DEFAULT_NAME = "SPHA Cover"

PLATFORM_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_PLATFORM): cv.string,
        vol.Required(CONF_MODULE_ID): cv.string,
        vol.Required(CONF_CHANNEL): cv.positive_int,
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    }
)


def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info=None,
) -> None:
    add_entities([SphaCover(config, hass.components.mqtt, hass)])


class Relay(SwitchEntity):
    def __init__(self, config, mqtt, hass):
        self._hass = hass
        self._mqtt = mqtt
        self._is_on = False
        self._state = None

        self._module_id = config["module_id"]
        self._relay = config["relay"]

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

    def turn_on(self, **kwargs) -> None:
        self._mqtt.publish(
            hass=self._hass,
            topic=self._command_topic,
            payload=json.dumps({"state": TURN_ON_PAYLOAD}),
        )

    def turn_off(self, **kwargs) -> None:
        self._mqtt.publish(
            hass=self._hass,
            topic=self._command_topic,
            payload=json.dumps({"state": TURN_OFF_PAYLOAD}),
        )


class SphaCover(CoverEntity):
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
            + str(config["module_id"] + "." + str(config["channel"]))
        )
        self._module_id = config["module_id"]
        self._channel = config["channel"]

        self._attr_is_closed = False

        self._close_relay = Relay(
            {"module_id": self._module_id, "relay": ((self._channel - 1) * 2) + 0},
            self._mqtt,
            self._hass,
        )

        self._open_relay = Relay(
            {"module_id": self._module_id, "relay": ((self._channel - 1) * 2) + 1},
            self._mqtt,
            self._hass,
        )

        # self._attr_supported_features = (
        #         CoverEntityFeature.OPEN
        #         | CoverEntityFeature.CLOSE
        #         | CoverEntityFeature.STOP
        #     )

    @property
    def supported_features(self) -> int:
        """Flag supported features."""
        if self._attr_supported_features is not None:
            return self._attr_supported_features

        supported_features = (
            CoverEntityFeature.OPEN | CoverEntityFeature.CLOSE | CoverEntityFeature.STOP
        )

        return supported_features

    @property
    def name(self):
        """Name of the device."""
        return self._name

    @property
    def unique_id(self):
        # TODO: get first part from domain
        return "spha.cover.{module_id}.{channel}".format(
            module_id=self._module_id, channel=self._channel
        )

    def open_cover(self, **kwargs) -> None:
        self._open_relay.turn_on()
        self._close_relay.turn_off()
        self._attr_is_opening = True
        self._attr_is_closing = False
        return True

    def close_cover(self, **kwargs) -> None:
        self._open_relay.turn_off()
        self._close_relay.turn_on()
        self._attr_is_opening = False
        self._attr_is_closing = True
        return True

    def stop_cover(self, **kwargs) -> None:
        self._open_relay.turn_off()
        self._close_relay.turn_off()
        self._attr_is_opening = False
        self._attr_is_closing = False
        return True
