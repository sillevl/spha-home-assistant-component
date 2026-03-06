import json
import logging

from homeassistant.components import mqtt
from homeassistant.components.light import ColorMode, LightEntity
from homeassistant.components.mqtt.models import ReceiveMessage
from homeassistant.core import HomeAssistant

import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType

from .const import (
    CONF_MODULE_ID,
    CONF_NAME,
    CONF_PLATFORM,
    CONF_RELAY,
    DEFAULT_LIGHT_NAME,
    DOMAIN,
    TOPIC_ACTION_RELAY,
    TOPIC_EVENT_RELAY,
    TURN_OFF_PAYLOAD,
    TURN_ON_PAYLOAD,
)
from .utils import parse_relay_state_payload

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_PLATFORM): cv.string,
        vol.Required(CONF_MODULE_ID): vol.Any(cv.string, cv.positive_int),
        vol.Required(CONF_RELAY): cv.positive_int,
        vol.Optional(CONF_NAME, default=DEFAULT_LIGHT_NAME): cv.string,
    }
)


def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info=None,
) -> None:
    add_entities([SphaLight(config, hass)])


class SphaLight(LightEntity):
    def __init__(self, config, hass):
        self._hass = hass
        self._state = False
        self._attr_supported_color_modes = {ColorMode.ONOFF}
        self._attr_color_mode = ColorMode.ONOFF
        self._attr_name = (
            config[CONF_NAME]
            if config[CONF_NAME] != DEFAULT_LIGHT_NAME
            else f"{DEFAULT_LIGHT_NAME} {config[CONF_MODULE_ID]}.{config[CONF_RELAY]}"
        )
        self._module_id = config[CONF_MODULE_ID]
        self._relay = config[CONF_RELAY]
        self._attr_unique_id = f"{DOMAIN}.light.{self._module_id}.{self._relay}"
        self._unsub_state = None
        # TODO: make first part topic configurable

        self._state_topic = TOPIC_EVENT_RELAY.format(
            module_id=self._module_id, relay=self._relay
        )
        self._command_topic = TOPIC_ACTION_RELAY.format(
            module_id=self._module_id, relay=self._relay
        )

    async def async_added_to_hass(self) -> None:
        self._unsub_state = await mqtt.async_subscribe(
            self._hass, self._state_topic, self._message_received
        )

    async def async_will_remove_from_hass(self) -> None:
        if self._unsub_state is not None:
            self._unsub_state()
            self._unsub_state = None

    def _message_received(self, msg: ReceiveMessage):
        """Handle MQTT state updates."""
        parsed_state = parse_relay_state_payload(msg.payload)
        if parsed_state is None:
            _LOGGER.debug(
                "Ignoring unsupported payload on %s: %s", self._state_topic, msg.payload
            )
            return

        if self._state != parsed_state:
            self._state = parsed_state
            self.async_write_ha_state()

    @property
    def name(self):
        """Name of the device."""
        return self._attr_name

    @property
    def unique_id(self):
        return self._attr_unique_id

    @property
    def is_on(self):
        """Return true if light is on."""
        return self._state

    def turn_off(self, **kwargs):
        """Turn the device off."""
        payload = {"state": TURN_OFF_PAYLOAD}
        mqtt.publish(
            hass=self._hass, topic=self._command_topic, payload=json.dumps(payload)
        )

    def turn_on(self, **kwargs):
        """Turn the device on."""
        payload = {"state": TURN_ON_PAYLOAD}
        mqtt.publish(
            hass=self._hass, topic=self._command_topic, payload=json.dumps(payload)
        )
