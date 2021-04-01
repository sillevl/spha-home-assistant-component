"""
The "hello world" custom component.
This component implements the bare minimum that a component should implement.
Configuration:
To use the hello_world component you will need to add the following to your
configuration.yaml file.
teletask_sillevl:
"""
import asyncio
from homeassistant.core import callback
from homeassistant.components import mqtt

import voluptuous as vol


# The domain of your component. Should be equal to the name of your component.
DOMAIN = "teletask_sillevl"

CONF_TOPIC = "topic"
DEFAULT_TOPIC = "home-assistant/mqtt_example"

# Schema to validate the configured MQTT topic
# CONFIG_SCHEMA = vol.Schema(
#     {vol.Optional(CONF_TOPIC, default=DEFAULT_TOPIC): mqtt.valid_subscribe_topic}
# )


@asyncio.coroutine
async def async_setup(hass, config):
    """Set up a skeleton component."""
    # States are in the format DOMAIN.OBJECT_ID.
    hass.states.async_set("teletask_sillevl.Hello_World", "Works!")

    """Set up the MQTT async example component."""
    topic = config[DOMAIN][CONF_TOPIC]
    entity_id = "mqtt_example.last_message"

    # Listen to a message on MQTT.
    @callback
    def message_received(topic, payload, qos):
        """A new MQTT message has been received."""
        print("message received !!!")
        hass.states.async_set(entity_id, payload)

    await hass.components.mqtt.async_subscribe(topic, message_received)

    hass.states.async_set(entity_id, "No messages")

    # Service to publish a message on MQTT.
    @callback
    def set_state_service(call):
        """Service to send a message."""
        hass.components.mqtt.async_publish(topic, call.data.get("new_state"))

    # Register our service with Home Assistant.
    hass.services.async_register(DOMAIN, "set_state", set_state_service)

    # Return boolean to indicate that initialization was successfully.
    return True


@asyncio.coroutine
async def async_setup_entry(hass, entry):
    print("---------------------------")
    print(entry)
    breakpoint()