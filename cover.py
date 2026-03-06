import json

from homeassistant.components import mqtt
from homeassistant.components.cover import CoverEntity, CoverEntityFeature
from homeassistant.core import HomeAssistant

import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType

from .const import (
    CONF_CHANNEL,
    CONF_MODULE_ID,
    CONF_NAME,
    CONF_PLATFORM,
    CONF_RELAY,
    DEFAULT_COVER_NAME,
    DOMAIN,
    TOPIC_ACTION_RELAY,
    TURN_OFF_PAYLOAD,
    TURN_ON_PAYLOAD,
)
from .utils import cover_channel_relays

PLATFORM_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_PLATFORM): cv.string,
        vol.Required(CONF_MODULE_ID): vol.Any(cv.string, cv.positive_int),
        vol.Required(CONF_CHANNEL): cv.positive_int,
        vol.Optional(CONF_NAME, default=DEFAULT_COVER_NAME): cv.string,
    }
)


def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info=None,
) -> None:
    add_entities([SphaCover(config, hass)])


class Relay:
    def __init__(self, config, hass):
        self._hass = hass
        self._module_id = config[CONF_MODULE_ID]
        self._relay = config[CONF_RELAY]
        self._command_topic = TOPIC_ACTION_RELAY.format(
            module_id=self._module_id, relay=self._relay
        )

    async def async_turn_on(self, **kwargs) -> None:
        await mqtt.async_publish(
            hass=self._hass,
            topic=self._command_topic,
            payload=json.dumps({"state": TURN_ON_PAYLOAD}),
        )

    async def async_turn_off(self, **kwargs) -> None:
        await mqtt.async_publish(
            hass=self._hass,
            topic=self._command_topic,
            payload=json.dumps({"state": TURN_OFF_PAYLOAD}),
        )


class SphaCover(CoverEntity):
    def __init__(self, config, hass):
        self._hass = hass
        self._attr_assumed_state = True
        self._attr_name = (
            config[CONF_NAME]
            if config[CONF_NAME] != DEFAULT_COVER_NAME
            else f"{DEFAULT_COVER_NAME} {config[CONF_MODULE_ID]}.{config[CONF_CHANNEL]}"
        )
        self._module_id = config[CONF_MODULE_ID]
        self._channel = config[CONF_CHANNEL]
        self._attr_unique_id = f"{DOMAIN}.cover.{self._module_id}.{self._channel}"

        self._attr_supported_features = (
            CoverEntityFeature.OPEN
            | CoverEntityFeature.CLOSE
            | CoverEntityFeature.STOP
        )
        self._attr_is_closed = False
        self._attr_is_opening = False
        self._attr_is_closing = False

        close_relay, open_relay = cover_channel_relays(self._channel)

        self._close_relay = Relay(
            {CONF_MODULE_ID: self._module_id, CONF_RELAY: close_relay},
            self._hass,
        )

        self._open_relay = Relay(
            {CONF_MODULE_ID: self._module_id, CONF_RELAY: open_relay},
            self._hass,
        )

    @property
    def name(self):
        """Name of the device."""
        return self._attr_name

    @property
    def unique_id(self):
        return self._attr_unique_id

    async def async_open_cover(self, **kwargs) -> None:
        await self._open_relay.async_turn_on()
        await self._close_relay.async_turn_off()
        self._attr_is_opening = True
        self._attr_is_closing = False
        self._attr_is_closed = False
        self.async_write_ha_state()

    async def async_close_cover(self, **kwargs) -> None:
        await self._open_relay.async_turn_off()
        await self._close_relay.async_turn_on()
        self._attr_is_opening = False
        self._attr_is_closing = True
        self._attr_is_closed = True
        self.async_write_ha_state()

    async def async_stop_cover(self, **kwargs) -> None:
        await self._open_relay.async_turn_off()
        await self._close_relay.async_turn_off()
        self._attr_is_opening = False
        self._attr_is_closing = False
        self.async_write_ha_state()
