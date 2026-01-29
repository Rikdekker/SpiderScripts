# Plan: ADA Bash → Python Conversion

## Overview

The ADA project (Advanced dCache API) is a ~3100-line Bash script providing a CLI for SURF's dCache storage system. This plan describes the conversion to a modern Python package that works both as a **CLI tool** and as a **Python library**.

## Location

The Python version will be developed in the `ada-python/` subfolder within the existing SpiderScripts repository. This allows the Bash and Python versions to coexist during development and migration:

```
SpiderScripts/
├── ada/                     # Existing Bash version (untouched)
├── ada-python/              # New Python version
│   ├── ...
├── tests/                   # Existing Bash tests (untouched)
├── CONVERSION_PLAN.md
└── README.md
```

Once the Python version is validated, the Bash version can be archived and `ada-python/` promoted to the root.

## Project Structure

```
ada-python/
├── pyproject.toml
├── README.md
├── LICENSE
├── src/ada/
│   ├── __init__.py              # Public API, version
│   ├── __main__.py              # python -m ada support
│   ├── exceptions.py            # Exception hierarchy
│   ├── utils.py                 # URL encoding, permission checks, JSON conversion
│   ├── state.py                 # ~/.ada/ state management (channels, requests.log)
│   ├── cli/
│   │   ├── __init__.py
│   │   ├── app.py               # Click group, global options, main()
│   │   ├── formatters.py        # Table/JSON output formatting
│   │   └── commands/
│   │       ├── namespace.py     # list, longlist, stat, mkdir, mv, delete
│   │       ├── labels.py        # setlabel, rmlabel, lslabel, findlabel
│   │       ├── xattr.py         # setxattr, rmxattr, lsxattr, findxattr
│   │       ├── staging.py       # stage, unstage, stat-request, delete-request
│   │       ├── events.py        # events, report-staged, channels, delete-channel
│   │       ├── info.py          # whoami, space, quota, viewtoken
│   │       └── checksum.py      # checksum
│   ├── core/
│   │   ├── client.py            # AdaClient — main library entry point
│   │   ├── api.py               # HTTP wrapper (httpx) with error mapping
│   │   ├── auth.py              # AuthProvider ABC + TokenAuth, NetrcAuth, ProxyAuth
│   │   ├── config.py            # Config loading (files, env vars)
│   │   └── models.py            # Dataclasses (FileInfo, BulkRequest, Channel, etc.)
│   ├── services/
│   │   ├── namespace.py         # File/directory operations
│   │   ├── labels.py            # Label operations
│   │   ├── xattr.py             # Extended attribute operations
│   │   ├── staging.py           # Stage/unstage/bulk operations
│   │   ├── events.py            # SSE event streaming
│   │   ├── checksum.py          # Checksum retrieval
│   │   └── system.py            # whoami, space, quota
│   └── tokens/
│       ├── jwt.py               # JWT/OIDC token decode
│       ├── macaroon.py          # Macaroon token decode
│       └── validator.py         # Token validation (expiry, permissions)
└── tests/
    ├── conftest.py
    ├── unit/                    # Pytest unit tests (mocked API)
    ├── integration/             # Pytest integration tests (live dCache)
    └── fixtures/                # Test data (tokens, API responses, configs)
```

## Architecture

### Dual-use Design: Library + CLI

The core is `AdaClient` in `core/client.py` — fully independent of the CLI:

```python
# As a library:
from ada import AdaClient

with AdaClient(api="https://...", tokenfile="/path/to/token") as client:
    files = client.list("/pnfs/data/mydir")
    client.stage("/pnfs/data/mydir/file.dat", lifetime="7D")
    info = client.whoami()
```

The CLI (`cli/`) is a thin layer that maps Click commands to `AdaClient` methods.

### Service Layer

Each feature group lives in a separate service module:
- **NamespaceService** — list, longlist, stat, mkdir, mv, delete (+ recursive traversal)
- **LabelService** — set, list, remove, find (with regex)
- **XattrService** — set, list, remove, find (with regex)
- **StagingService** — stage, unstage, bulk requests, status
- **EventService** — SSE subscriptions, channel management
- **ChecksumService** — MD5/Adler32 retrieval
- **SystemService** — whoami, space, quota

### HTTP Layer (`core/api.py`)

Wraps `httpx` with:
- Automatic URL encoding of dCache paths
- HTTP status → exception mapping (401→AuthError, 403→ForbiddenError, 404→NotFoundError)
- Debug logging of all requests/responses
- SSE streaming support for events

### Authentication (`core/auth.py`)

Strategy pattern with `AuthProvider` ABC:
- **TokenAuth** — Bearer token (JWT or Macaroon), direct or from file
- **NetrcAuth** — Username/password via .netrc
- **ProxyAuth** — X.509 proxy certificate

Precedence (identical to Bash):
1. CLI arguments (highest)
2. Environment variables (`$BEARER_TOKEN`, `$ada_tokenfile`, etc.)
3. Config files (lowest)

Security checks preserved: files must not be world-readable/writable.

### Error Handling

Exception hierarchy:
```
AdaError (base)
├── AdaConfigError          — Invalid configuration
├── AdaSecurityError        — World-readable credentials etc.
├── AdaAuthError            — Auth setup errors
│   ├── AdaTokenExpiredError    — Token expired
│   └── AdaTokenPermissionError — Token missing permissions
├── AdaAuthenticationError  — Server rejected credentials (401)
├── AdaAPIError             — dCache API error (with status_code)
│   ├── AdaNotFoundError    — 404
│   └── AdaForbiddenError   — 403
├── AdaPathError            — Invalid path or type mismatch
└── AdaValidationError      — Input validation error
```

All Bash error messages are preserved, including:
- Token expiry warnings (< 60 seconds)
- Staging permission hints (storage.stage scope, bulk directory expansion)
- Recursive mkdir limits (max 10)
- Destructive operation confirmations

### Configuration (`core/config.py`)

- Same file format as Bash (`key=value`), so existing `~/.ada/ada.conf` files continue to work
- Search paths: `<package>/etc/ada.conf` → `/etc/ada.conf` → `~/.ada/ada.conf`
- Environment variables override file values
- `@dataclass` instead of pydantic (minimal dependencies)

## CLI Command Mapping

| Bash syntax | Python CLI |
|---|---|
| `ada --list /path` | `ada list /path` |
| `ada --longlist /path` | `ada longlist /path` |
| `ada --stat /path` | `ada stat /path` |
| `ada --mkdir /path --recursive` | `ada mkdir /path --recursive` |
| `ada --mv /src /dst` | `ada mv /src /dst` |
| `ada --delete /path --recursive --force` | `ada delete /path --recursive --force` |
| `ada --setlabel /path label` | `ada setlabel /path label` |
| `ada --rmlabel /path label` | `ada rmlabel /path label` |
| `ada --lslabel /path [label]` | `ada lslabel /path [label]` |
| `ada --findlabel /dir regex --recursive` | `ada findlabel /dir regex --recursive` |
| `ada --setxattr /path attrs.txt` | `ada setxattr /path attrs.txt` |
| `ada --rmxattr /path key` | `ada rmxattr /path key` |
| `ada --lsxattr /path [key]` | `ada lsxattr /path [key]` |
| `ada --findxattr /dir key regex --recursive` | `ada findxattr /dir key regex --recursive` |
| `ada --checksum /path --recursive` | `ada checksum /path --recursive` |
| `ada --stage /path --lifetime 7D` | `ada stage /path --lifetime 7D` |
| `ada --stage --from-file list.txt` | `ada stage --from-file list.txt` |
| `ada --unstage /path` | `ada unstage /path` |
| `ada --stat-request id` | `ada stat-request id` |
| `ada --delete-request id` | `ada delete-request id` |
| `ada --events chan /path --recursive` | `ada events chan /path --recursive` |
| `ada --report-staged chan /path` | `ada report-staged chan /path` |
| `ada --channels [name]` | `ada channels [name]` |
| `ada --delete-channel name` | `ada delete-channel name` |
| `ada --space [poolgroup]` | `ada space [poolgroup]` |
| `ada --quota` | `ada quota` |
| `ada --whoami` | `ada whoami` |
| `ada --viewtoken` | `ada viewtoken` |

## Dependencies

| Package | Reason |
|---|---|
| `httpx>=0.27` | HTTP client with sync+async, streaming SSE, type hints |
| `click>=8.1` | CLI framework for 25+ commands, CliRunner for testing |

Dev dependencies: `pytest`, `pytest-asyncio`, `respx` (httpx mocking), `ruff`, `mypy`

## Implementation Phases

1. **Phase 1 — Foundation**: `exceptions.py`, `models.py`, `config.py`, `utils.py`
2. **Phase 2 — Auth & HTTP**: `tokens/`, `auth.py`, `api.py`
3. **Phase 3 — Core Services**: `namespace.py`, `system.py`, `checksum.py`
4. **Phase 4 — Advanced Services**: `labels.py`, `xattr.py`, `staging.py`
5. **Phase 5 — Client & CLI**: `client.py`, `app.py`, all command modules
6. **Phase 6 — Events**: `events.py`, `state.py` (most complex: SSE streaming)
7. **Phase 7 — Polish**: Output formatters, tests, CI/CD, `pyproject.toml`

## Verification

- **Unit tests**: `pytest tests/unit/` — all services mocked, token validation, config loading, CLI parsing
- **Integration tests**: `pytest tests/integration/ -m integration` — live dCache (same scenarios as existing `integration_test.sh`)
- **Type checking**: `mypy src/ada/`
- **Linting**: `ruff check src/`
- **CLI smoke test**: `ada --version`, `ada whoami`, `ada list /pnfs/...`

## Key Files (Current Bash Version)

- `ada/ada` — Complete Bash source (~3100 lines), all business logic
- `ada/etc/ada.conf` — Default config (format to be preserved)
- `tests/unit_test.sh` — Existing unit tests (behavior to replicate)
- `tests/integration_test.sh` — Acceptance criteria for the port
