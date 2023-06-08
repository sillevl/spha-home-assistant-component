"""
The "hello world" custom component.
This component implements the bare minimum that a component should implement.
Configuration:
To use the hello_world component you will need to add the following to your
configuration.yaml file.
teletask_sillevl:
"""
import asyncio

# The domain of your component. Should be equal to the name of your component.
DOMAIN = "teletask_sillevl"

async def async_setup(hass, config):
    # print(config[DOMAIN]["light"])
    return True
