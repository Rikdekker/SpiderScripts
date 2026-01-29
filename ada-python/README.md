# ADA - Advanced dCache API (Python)

Python implementation of the ADA tool for managing data in SURF's dCache storage system.

## Installation

```bash
pip install -e ".[dev]"
```

## Usage

### As a CLI tool

```bash
ada --tokenfile /path/to/token whoami
ada --tokenfile /path/to/token list /pnfs/data/mydir
ada --tokenfile /path/to/token stage /pnfs/data/mydir/file.dat --lifetime 7D
```

### As a Python library

```python
from ada import AdaClient

with AdaClient(api="https://...", tokenfile="/path/to/token") as client:
    files = client.list("/pnfs/data/mydir")
    client.stage("/pnfs/data/mydir/file.dat", lifetime="7D")
    info = client.whoami()
```

## Development

```bash
pip install -e ".[dev]"
pytest
ruff check src/
mypy src/ada/
```
