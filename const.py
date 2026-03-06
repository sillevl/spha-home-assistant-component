"""Constants for the SPHA integration."""

DOMAIN = "spha"

TURN_ON_PAYLOAD = "on"
TURN_OFF_PAYLOAD = "off"

TOPIC_EVENT_RELAY = "sixpack/event/relay/{module_id}/{relay}"
TOPIC_ACTION_RELAY = "sixpack/action/relay/{module_id}/{relay}"

CONF_PLATFORM = "platform"
CONF_NAME = "name"
CONF_MODULE_ID = "module_id"
CONF_RELAY = "relay"
CONF_CHANNEL = "channel"

DEFAULT_LIGHT_NAME = "SPHA Light"
DEFAULT_COVER_NAME = "SPHA Cover"
