# Configuration

## Config File Format

ADA uses a simple `key=value` format, compatible with the original Bash version. Existing `~/.ada/ada.conf` files work without changes.

```ini
# ADA configuration
api=https://dcacheview.grid.surfsara.nl:22880/api/v1
igtf=true
channel_timeout=3600
```

Lines starting with `#` are comments. Bash-style array syntax (used in the Bash version for curl options) is ignored.

## Config File Locations

Config files are loaded in order, with later files overriding earlier values:

| Priority | Path | Description |
|----------|------|-------------|
| 1 (lowest) | `<package>/etc/ada.conf` | Bundled defaults |
| 2 | `/etc/ada.conf` | System-wide config |
| 3 (highest) | `~/.ada/ada.conf` | User-level config |

## Configuration Options

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `api` | string | (from bundled config) | dCache API URL (must start with `https://` and end with `/api/v1` or `/api/v2`) |
| `igtf` | boolean | `true` | Use IGTF Grid certificates for proxy auth |
| `channel_timeout` | integer | `3600` | Default SSE channel timeout in seconds |
| `debug` | boolean | `false` | Enable debug logging |
| `tokenfile` | string | — | Default token file path |
| `netrcfile` | string | — | Default netrc file path |

## Environment Variables

Environment variables override config file values. They are checked after loading config files but before applying explicit CLI arguments.

| Variable | Overrides | Description |
|----------|-----------|-------------|
| `ada_api` | `api` | dCache API URL |
| `ada_debug` | `debug` | Enable debug output (`true`/`false`) |
| `ada_channel_timeout` | `channel_timeout` | SSE channel timeout |
| `ada_igtf` | `igtf` | Use IGTF certificates |
| `ada_tokenfile` | `tokenfile` | Token file path |
| `ada_netrcfile` | `netrcfile` | Netrc file path |
| `BEARER_TOKEN` | — | Direct bearer token string (used by auth resolver) |
| `X509_USER_PROXY` | — | X.509 proxy file path |
| `X509_CERT_DIR` | — | Grid certificate directory |

## Overall Precedence

The full precedence chain, from lowest to highest:

```
Bundled config → /etc/ada.conf → ~/.ada/ada.conf → Environment vars → CLI arguments
```

## Example Setup

Minimal setup to avoid passing arguments every time:

```bash
# Create config directory
mkdir -p ~/.ada
chmod 700 ~/.ada

# Create config file
cat > ~/.ada/ada.conf << 'EOF'
api=https://dcacheview.grid.surfsara.nl:22880/api/v1
EOF

# Store your token
echo "your-bearer-token-here" > ~/.ada/token
chmod 600 ~/.ada/token

# Point to it in config
echo "tokenfile=$HOME/.ada/token" >> ~/.ada/ada.conf
```

Now you can use ADA without any arguments:

```bash
ada whoami
ada list /pnfs/grid.sara.nl/data/myproject
```

## Library Configuration

When using ADA as a library, you can pass custom config paths:

```python
from ada import AdaClient

# Use default config file search
client = AdaClient()

# Use custom config paths
client = AdaClient(config_paths=["/custom/path/ada.conf"])

# Override everything explicitly (ignores config files for these values)
client = AdaClient(
    api="https://dcacheview.grid.surfsara.nl:22880/api/v1",
    tokenfile="/path/to/token",
    debug=True,
)
```

Explicit constructor arguments always have the highest priority.
