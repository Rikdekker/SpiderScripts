# Getting Started

## Requirements

- Python 3.10 or higher
- Access to a dCache instance with a valid API endpoint
- Authentication credentials (token, netrc, or X.509 proxy)

## Installation

### From source (development)

```bash
cd ada-python

# Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install ADA with development dependencies
pip install -e ".[dev]"
```

This installs ADA in editable mode along with development dependencies (pytest, ruff, mypy).

> **Note:** On macOS (and other systems with PEP 668), `pip install` outside a
> virtual environment is blocked. Always create a venv first.

### Dependencies

ADA has only two runtime dependencies:

| Package | Version | Purpose |
|---------|---------|---------|
| `httpx` | ≥0.27 | HTTP client with sync/async support and SSE streaming |
| `click` | ≥8.1 | CLI framework for 25+ commands |

## Verify Installation

```bash
# Verify ada points to the Python version (not an older Bash version)
which ada    # should show .venv/bin/ada

# Check the CLI is available
ada --version

# Check Python import works
python3 -c "from ada import AdaClient; print('OK')"
```

> **Tip:** If `which ada` shows a different path (e.g., `/usr/local/bin/ada`),
> an older Bash version of ada may take precedence. Ensure the virtual
> environment is activated, or remove/rename the old script.

## First Steps

### 1. Set up authentication

The simplest method is a bearer token file:

```bash
# Plain token file (one line with the token)
echo "your-bearer-token-here" > ~/.ada/token

# Or an rclone-style config file
cat > ~/.ada/token << EOF
[dcache]
type = webdav
url = https://webdav.grid.surfsara.nl
bearer_token = your-bearer-token-here
EOF
```

### 2. Check your identity

```bash
ada --tokenfile ~/.ada/token whoami
```

Output:
```
Status:   AUTHENTICATED
Username: user123
UID:      1234
GIDs:     5678
Home:     /pnfs/grid.sara.nl/data/user123
```

### 3. List a directory

```bash
ada --tokenfile ~/.ada/token list /pnfs/grid.sara.nl/data/myproject
```

### 4. Use as a library

```python
from ada import AdaClient

with AdaClient(
    api="https://dcacheview.grid.surfsara.nl:22880/api/v1",
    tokenfile="~/.ada/token"
) as client:
    # List a directory
    files = client.list("/pnfs/grid.sara.nl/data/myproject")
    for f in files:
        print(f)

    # Get detailed file info
    info = client.stat("/pnfs/grid.sara.nl/data/myproject/data.csv")
    print(f"Size: {info.size}, QoS: {info.current_qos}")
```

## Configuration File

Create `~/.ada/ada.conf` to avoid passing `--api` and `--tokenfile` every time:

```ini
api=https://dcacheview.grid.surfsara.nl:22880/api/v1
tokenfile=/home/user/.ada/token
```

Then simply:

```bash
ada whoami
ada list /pnfs/data/myproject
```

See [Configuration](configuration.md) for all options.
