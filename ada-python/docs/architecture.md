# Architecture

## Design Principles

1. **Dual-use**: Works as both a CLI tool and an importable Python library
2. **Separation of concerns**: CLI is a thin layer over the library; no business logic in CLI code
3. **Faithful port**: All error messages, validation rules, and behaviors from the Bash version are preserved
4. **Minimal dependencies**: Only `httpx` and `click` at runtime
5. **Type safety**: Full type hints throughout, compatible with mypy strict mode

## Project Structure

```
ada-python/
├── pyproject.toml               # Package metadata, dependencies, entry points
├── src/ada/
│   ├── __init__.py              # Public API: AdaClient + all exceptions
│   ├── __main__.py              # python -m ada support
│   ├── exceptions.py            # Exception hierarchy (11 exception types)
│   ├── models.py                # Frozen dataclasses (FileInfo, BulkRequest, etc.)
│   ├── config.py                # Config loading (files, env vars, precedence)
│   ├── utils.py                 # URL encoding, permissions, parsing helpers
│   ├── state.py                 # ~/.ada/ state management (channels, logs)
│   │
│   ├── core/                    # Foundation layer
│   │   ├── client.py            # AdaClient — main library entry point
│   │   ├── api.py               # DcacheAPI — HTTP wrapper (httpx)
│   │   └── auth.py              # AuthProvider ABC + TokenAuth, NetrcAuth, ProxyAuth
│   │
│   ├── services/                # Business logic layer (one module per feature)
│   │   ├── namespace.py         # File/directory operations
│   │   ├── labels.py            # Label management
│   │   ├── xattr.py             # Extended attribute management
│   │   ├── staging.py           # Tape staging/unstaging
│   │   ├── events.py            # SSE event streaming
│   │   ├── checksum.py          # Checksum retrieval
│   │   └── system.py            # whoami, space, quota
│   │
│   ├── tokens/                  # Token handling (JWT + Macaroon)
│   │   ├── jwt.py               # JWT/OIDC decode and inspection
│   │   ├── macaroon.py          # Macaroon decode and inspection
│   │   └── validator.py         # Token validation (expiry, permissions)
│   │
│   └── cli/                     # CLI layer (thin wrapper over library)
│       ├── app.py               # Click group, global options, command registration
│       ├── formatters.py        # Output formatting (tables, human-readable sizes)
│       └── commands/            # One module per command group
│           ├── namespace.py     # list, longlist, stat, mkdir, mv, delete
│           ├── labels.py        # setlabel, lslabel, rmlabel, findlabel
│           ├── xattr.py         # setxattr, lsxattr, rmxattr, findxattr
│           ├── staging.py       # stage, unstage, stat-request, delete-request
│           ├── events.py        # events, report-staged, channels, delete-channel
│           ├── info.py          # whoami, viewtoken, space, quota
│           └── checksum.py      # checksum
│
└── tests/
    ├── conftest.py              # Shared fixtures (mock API, sample responses, JWT factory)
    └── unit/                    # Unit tests (65 tests)
        ├── test_utils.py        # URL encoding, lifetime parsing, JSON conversion
        ├── test_tokens.py       # JWT/Macaroon validation, expiry, permissions
        ├── test_namespace.py    # File operations (list, stat, mkdir, mv, delete)
        ├── test_config.py       # Config loading, env vars, file parsing
        └── test_cli.py          # CLI commands, help, version
```

## Layer Architecture

```
┌─────────────────────────────────────────────┐
│  CLI Layer (cli/)                            │  Click commands, output formatting
│  Thin wrapper — no business logic            │
├─────────────────────────────────────────────┤
│  Client Layer (core/client.py)               │  AdaClient: public API surface
│  Composes services, validates auth           │  Used by both CLI and library consumers
├─────────────────────────────────────────────┤
│  Service Layer (services/)                   │  Business logic per feature domain
│  namespace, labels, xattr, staging,          │  Each service receives DcacheAPI
│  events, checksum, system                    │
├─────────────────────────────────────────────┤
│  HTTP Layer (core/api.py)                    │  DcacheAPI: httpx wrapper
│  URL encoding, error mapping, SSE streaming  │  Maps HTTP status → exceptions
├─────────────────────────────────────────────┤
│  Auth Layer (core/auth.py)                   │  Strategy pattern (AuthProvider ABC)
│  TokenAuth, NetrcAuth, ProxyAuth             │  Credential resolution + validation
├─────────────────────────────────────────────┤
│  Foundation (exceptions, models, config,     │  Shared infrastructure
│  utils, state, tokens/)                      │  No dependencies on upper layers
└─────────────────────────────────────────────┘
```

## Key Design Decisions

### Why httpx instead of requests?

- Built-in streaming support for SSE (Server-Sent Events), critical for the `events` and `report-staged` commands
- Native async support (ready for future async operations)
- Type hints throughout the API
- Modern Python (supports HTTP/2)

### Why Click instead of argparse?

- 25+ commands are cleanly organized as decorated functions
- Built-in `CliRunner` for testing CLI commands without subprocess
- Automatic help generation with proper formatting
- Composable groups and shared context for global options

### Why frozen dataclasses instead of pydantic?

- Zero additional dependencies
- Sufficient for our data models (simple value objects)
- Frozen (immutable) enforces correct usage patterns
- Compatible with Python 3.10+ without extras

### Why services use lazy namespace loading?

Several services (labels, xattr, checksum, staging) need `NamespaceService` for path type checks. To avoid circular imports and heavy initialization, they use lazy loading:

```python
def _get_namespace(self) -> NamespaceService:
    if self._namespace is None:
        from ada.services.namespace import NamespaceService
        self._namespace = NamespaceService(self._api)
    return self._namespace
```

When created via `AdaClient`, the namespace is passed directly and shared across all services.

### Why CLI commands use lazy imports?

CLI command functions import `get_client` inside the function body rather than at module level. This avoids importing the full library stack when Click only needs to parse `--help`:

```python
@click.command()
@click.pass_context
def whoami(ctx):
    from ada.cli.app import get_client  # Lazy import
    with get_client(ctx) as client:
        info = client.whoami()
```

## Mapping from Bash

| Bash Construct | Python Equivalent |
|---|---|
| `curl` with `jq` | `httpx` client with JSON parsing |
| `case/esac` argument parsing | Click decorators |
| `echo 1>&2 "ERROR: ..."` | Exception raising + CLI error handler |
| Temp files for auth headers | In-memory `Authorization` header |
| `trap` cleanup on EXIT | Context manager (`__exit__`) |
| `$dry_run` mode | Mock-based unit tests (no dry-run needed) |
| `shunit2` tests | pytest |
| Bash functions | Service class methods |
| Global variables | Dataclass instances |
| `~/.ada/` directory | `AdaState` class |
