# ADA Python Documentation

ADA (Advanced dCache API) is a tool for managing data stored in SURF's dCache storage system. This Python implementation provides both a **command-line interface** and a **Python library** for programmatic access.

## Table of Contents

- [Getting Started](getting-started.md) — Installation and first steps
- [CLI Reference](cli-reference.md) — All CLI commands and options
- [Library Reference](library-reference.md) — Using ADA as a Python library
- [Authentication](authentication.md) — Token, netrc, and proxy authentication
- [Configuration](configuration.md) — Config files and environment variables
- [Architecture](architecture.md) — Project structure and design decisions
- [Error Handling](error-handling.md) — Exception hierarchy and error recovery

## Quick Start

### As a CLI tool

```bash
pip install -e .
ada --tokenfile /path/to/token whoami
ada --tokenfile /path/to/token list /pnfs/data/mydir
```

### As a Python library

```python
from ada import AdaClient

with AdaClient(api="https://dcacheview.grid.surfsara.nl:22880/api/v1",
               tokenfile="/path/to/token") as client:
    files = client.list("/pnfs/data/mydir")
    info = client.whoami()
    print(f"Logged in as: {info.username}")
```
