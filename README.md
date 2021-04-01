# Teletask Home Assistant Integration

Only supports lights (relay) at the moment. Use with <https://github.com/sillevl/teletask-mqtt/>

## Configuration

Example configuration for `configuration.yaml`

```yaml
# Enable the integration by adding a 'teletask_sillevl' object
teletask_sillevl:

light:
  - platform: teletask_sillevl
    name: Aanbouw
    number: 47
  - platform: teletask_sillevl
    name: Bureau
    number: 46
  - platform: teletask_sillevl
    number: 48
```