# Authentication

ADA supports three authentication methods, matching the original Bash version.

## Precedence

When multiple credentials are available, ADA resolves authentication in this order (highest priority first):

1. **Explicit arguments** — `--tokenfile`, `--token`, `--netrc`, `--proxy` (CLI) or constructor parameters (library)
2. **Environment variables** — `$BEARER_TOKEN`, `$ada_tokenfile`, `$ada_netrcfile`
3. **Config file values** — `tokenfile=` or `netrcfile=` in `ada.conf`

## Method 1: Bearer Token

The most common method. Supports both JWT/OIDC tokens and Macaroon tokens.

### Token file (recommended)

```bash
# CLI
ada --tokenfile /path/to/token whoami

# Or via environment variable
export ada_tokenfile=/path/to/token
ada whoami
```

```python
# Library
client = AdaClient(tokenfile="/path/to/token")
```

The token file can be in two formats:

**Plain token** — a single line containing the token:
```
eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...
```

**rclone config** — the token is extracted from the `bearer_token` field:
```ini
[dcache]
type = webdav
url = https://webdav.grid.surfsara.nl
bearer_token = eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Direct token

```bash
# CLI via environment variable
export BEARER_TOKEN=eyJhbGciOiJSUzI1NiIs...
ada whoami

# CLI via argument
ada --token "eyJhbGciOiJSUzI1NiIs..." whoami
```

```python
# Library
client = AdaClient(token="eyJhbGciOiJSUzI1NiIs...")
```

### Token validation

ADA validates tokens before use:

- **Expiry check**: Token must be valid for at least 60 seconds
- **Permission check**: For staging operations, JWT tokens need `storage.stage` in their scope, and Macaroons need the `STAGE` activity permission
- **Inspect token**: Use `ada viewtoken` to decode and display token properties

## Method 2: Netrc (Basic Auth)

Username/password authentication using a standard `.netrc` file.

```bash
# CLI (uses ~/.netrc by default)
ada --netrc whoami

# CLI with custom path
ada --netrc /path/to/netrc whoami
```

```python
# Library
client = AdaClient(netrc="/path/to/netrc")
```

The netrc file format:
```
machine dcacheview.grid.surfsara.nl
login myusername
password mypassword
```

## Method 3: X.509 Proxy Certificate

Grid certificate authentication for environments with VOMS proxy support.

```bash
# CLI (uses default proxy location)
ada --proxy whoami

# CLI with custom proxy file
ada --proxy /tmp/x509up_u1000 whoami
```

```python
# Library
client = AdaClient(proxy="/path/to/proxy")
```

The proxy file is typically at `/tmp/x509up_u<UID>` and created with `voms-proxy-init`.

### IGTF Certificates

By default, ADA uses IGTF Grid certificates from `/etc/grid-security/certificates`. Disable with:

```bash
ada --no-igtf --proxy whoami
```

```python
client = AdaClient(proxy="/path/to/proxy", igtf=False)
```

## Security Checks

ADA enforces security on credential files, matching the Bash version:

- **Token files** must not be world-readable or world-writable
- **Netrc files** must not be world-readable or world-writable
- **Config files** must not be world-writable

If a file has insecure permissions, ADA raises `AdaSecurityError` with instructions to fix:

```
ERROR: File '/home/user/.ada/token' is world readable.
Fix with: chmod o-r '/home/user/.ada/token'
```

Fix with:
```bash
chmod 600 ~/.ada/token
chmod 600 ~/.netrc
```
