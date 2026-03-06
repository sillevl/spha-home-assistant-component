# SPHA - SixPack Home Automation Home Assistant Integration

Supports:
- Lights (single relay)
- Covers (paired relays per channel)

Use with <https://github.com/sillevl/teletask-mqtt/>.

## Configuration

Example configuration for `configuration.yaml`

```yaml
# Enable the integration root object
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

cover:
  - platform: spha
    name: Living Room Shutter
    module_id: 47
    channel: 1
```

## Testing

Install test dependencies:

```bash
pip install -r requirements-dev.txt
```

Run tests:

```bash
pytest -q
```