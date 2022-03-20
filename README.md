# SPHA - SixPack Home Automation Home Assistant Integration

Only supports lights (relay) at the moment. Use with <https://github.com/sillevl/teletask-mqtt/>

## Configuration

Example configuration for `configuration.yaml`

```yaml
# Enable the integration by adding a 'teletask_sillevl' object
spha:

light:
  - platform: spha
    name: Aanbouw
    module_id: 47
    relay: 1
  - platform: spha
    name: Bureau
    module_id: 46
    relay: 2
  - platform: spha
    module_id: 48
    relay: 3
```