# Library Reference

ADA can be used as a Python library by importing `AdaClient`. This gives full programmatic access to all dCache operations without going through the CLI.

## AdaClient

The main entry point. Instantiate with authentication credentials, then call methods to interact with dCache.

### Constructor

```python
from ada import AdaClient

client = AdaClient(
    api="https://dcacheview.grid.surfsara.nl:22880/api/v1",  # API URL
    tokenfile="/path/to/token",   # Token file (rclone or plain)
    token=None,                   # Or: direct bearer token string
    netrc=None,                   # Or: netrc file path
    proxy=None,                   # Or: X.509 proxy file path
    igtf=True,                    # Use IGTF Grid certificates
    config_paths=None,            # Custom config file paths
    debug=False,                  # Enable debug logging
)
```

All authentication parameters are optional — the client resolves credentials from arguments, environment variables, and config files (in that order).

### Context Manager

Always use `AdaClient` as a context manager to ensure the HTTP connection is properly closed:

```python
with AdaClient(tokenfile="/path/to/token") as client:
    files = client.list("/pnfs/data/mydir")
```

Or manually close:

```python
client = AdaClient(tokenfile="/path/to/token")
try:
    files = client.list("/pnfs/data/mydir")
finally:
    client.close()
```

## Namespace Operations

### `client.list(path) -> list[str]`

List directory contents. Returns sorted file names with `/` appended for directories.

```python
items = client.list("/pnfs/data/mydir")
# ['file1.txt', 'file2.dat', 'subdir/']
```

### `client.longlist(paths) -> list[FileInfo]`

Get detailed file information. Accepts a single path or list of paths.

```python
files = client.longlist("/pnfs/data/mydir")
for f in files:
    print(f"{f.path}: {f.size} bytes, {f.locality}")
```

### `client.stat(path) -> FileInfo`

Get complete metadata for a single file or directory.

```python
info = client.stat("/pnfs/data/mydir/file.dat")
print(f"PNFS ID: {info.pnfs_id}")
print(f"Size: {info.size}")
print(f"QoS: {info.current_qos}")
print(f"Locality: {info.locality}")
print(f"Labels: {info.labels}")
print(f"Xattr: {info.extended_attributes}")
print(f"Checksums: {info.checksums}")
```

### `client.mkdir(path, recursive=False) -> str`

Create a directory. Returns `"created"` or `"already exists"`.

```python
client.mkdir("/pnfs/data/mydir/newdir")
client.mkdir("/pnfs/data/mydir/a/b/c", recursive=True)
```

### `client.mv(source, destination) -> str`

Move or rename a file or directory.

```python
client.mv("/pnfs/data/oldname", "/pnfs/data/newname")
```

### `client.delete(path, recursive=False, force=False)`

Delete a file or directory.

```python
client.delete("/pnfs/data/file.dat")
client.delete("/pnfs/data/mydir", recursive=True, force=True)
```

## Label Operations

### `client.set_label(path, label) -> str`

```python
client.set_label("/pnfs/data/file.dat", "important")
```

### `client.list_labels(path, label=None) -> list[str]`

```python
labels = client.list_labels("/pnfs/data/file.dat")
# ['important', 'processed']
```

### `client.remove_label(path, label="", all=False) -> str`

```python
client.remove_label("/pnfs/data/file.dat", label="important")
client.remove_label("/pnfs/data/file.dat", all=True)
```

### `client.find_label(path, regex, recursive=False) -> list[tuple[str, list[str]]]`

```python
results = client.find_label("/pnfs/data/mydir", "import.*", recursive=True)
for file_path, matching_labels in results:
    print(f"{file_path}: {matching_labels}")
```

## Extended Attribute Operations

### `client.set_xattr(path, attributes) -> str`

Accepts a dict or a string (JSON / key=value format).

```python
client.set_xattr("/pnfs/data/file.dat", {"project": "spider", "batch": "42"})
client.set_xattr("/pnfs/data/file.dat", "project=spider,batch=42")
```

### `client.list_xattr(path, key=None) -> dict[str, str]`

```python
attrs = client.list_xattr("/pnfs/data/file.dat")
# {'project': 'spider', 'batch': '42'}

value = client.list_xattr("/pnfs/data/file.dat", key="project")
# {'project': 'spider'}
```

### `client.remove_xattr(path, key="", all=False) -> str`

```python
client.remove_xattr("/pnfs/data/file.dat", key="batch")
client.remove_xattr("/pnfs/data/file.dat", all=True)
```

### `client.find_xattr(path, key, regex, recursive=False, all_keys=False) -> list[tuple[str, dict[str, str]]]`

```python
results = client.find_xattr("/pnfs/data/mydir", "project", "spider.*", recursive=True)
for file_path, matching_attrs in results:
    print(f"{file_path}: {matching_attrs}")
```

## Checksum Operations

### `client.checksum(paths, recursive=False, from_file=None) -> list[Checksum]`

```python
checksums = client.checksum("/pnfs/data/file.dat")
for cs in checksums:
    print(f"{cs.checksum_type}: {cs.value}")

# Recursive
checksums = client.checksum("/pnfs/data/mydir", recursive=True)

# From file list
checksums = client.checksum([], from_file="paths.txt")
```

## Staging Operations

### `client.stage(paths, recursive=False, lifetime="7D", from_file=None) -> BulkRequest`

Bring files from tape to disk. Validates token permissions before staging.

```python
request = client.stage("/pnfs/data/file.dat", lifetime="7D")
print(f"Request ID: {request.request_id}")
print(f"Targets: {len(request.targets)}")

# Recursive staging
request = client.stage("/pnfs/data/mydir", recursive=True, lifetime="14D")

# From file list
request = client.stage([], from_file="filelist.txt")
```

### `client.unstage(paths, recursive=False, request_id=None, from_file=None) -> BulkRequest`

Release disk copies.

```python
request = client.unstage("/pnfs/data/file.dat")
```

### `client.stat_request(request_id) -> BulkRequestStatus`

```python
status = client.stat_request("abc-123-def-456")
print(f"Status: {status.status}")
for target in status.targets:
    print(f"  {target}")
```

### `client.delete_request(request_id)`

```python
client.delete_request("abc-123-def-456")
```

## System Information

### `client.whoami() -> UserInfo`

```python
info = client.whoami()
print(f"Username: {info.username}")
print(f"UID: {info.uid}")
print(f"Home: {info.home}")
```

### `client.space(poolgroup=None) -> SpaceInfo | list[str]`

```python
# List pool groups
groups = client.space()

# Get space for a specific group
space = client.space("my-pool-group")
print(f"Total: {space.total}, Free: {space.free}")
```

### `client.quota() -> list[QuotaInfo]`

```python
quotas = client.quota()
for q in quotas:
    print(f"{q.quota_type}: disk={q.replica}/{q.replica_limit}, tape={q.custodial}/{q.custodial_limit}")
```

### `client.view_token() -> dict`

```python
token_info = client.view_token()
print(token_info)  # Decoded JWT or Macaroon properties
```

## Data Models

All return types are frozen dataclasses defined in `ada.models`:

### `FileInfo`

```python
@dataclass(frozen=True)
class FileInfo:
    path: str
    file_type: FileType          # REGULAR, DIR, LINK
    size: Optional[int]
    mtime: Optional[datetime]
    pnfs_id: Optional[str]
    current_qos: Optional[str]
    target_qos: Optional[str]
    locality: Optional[Locality]  # ONLINE, NEARLINE, ONLINE_AND_NEARLINE, UNAVAILABLE
    labels: tuple[str, ...]
    extended_attributes: dict[str, str]
    checksums: tuple[Checksum, ...]
```

### `Checksum`

```python
@dataclass(frozen=True)
class Checksum:
    path: str
    checksum_type: str   # "ADLER32" or "MD5_TYPE"
    value: str
```

### `BulkRequest`

```python
@dataclass(frozen=True)
class BulkRequest:
    request_id: str
    request_url: str
    activity: str        # "PIN" or "UNPIN"
    targets: tuple[str, ...]
```

### `BulkRequestStatus`

```python
@dataclass(frozen=True)
class BulkRequestStatus:
    uid: str
    status: str
    targets: tuple[dict, ...]
    raw: dict            # Full API response
```

### `UserInfo`

```python
@dataclass(frozen=True)
class UserInfo:
    status: str
    uid: Optional[int]
    gids: tuple[int, ...]
    username: Optional[str]
    home: Optional[str]
    root: Optional[str]
    raw: dict            # Full API response
```

### `SpaceInfo`

```python
@dataclass(frozen=True)
class SpaceInfo:
    total: int
    free: int
    precious: int
    removable: int
```

### `QuotaInfo`

```python
@dataclass(frozen=True)
class QuotaInfo:
    quota_type: str      # "user" or "group"
    id: int
    custodial: int
    custodial_limit: Optional[int]
    replica: int
    replica_limit: Optional[int]
```

## Service Access

For advanced use cases, you can access individual services directly:

```python
with AdaClient(tokenfile="/path/to/token") as client:
    # Direct service access
    subdirs = client.namespace.get_subdirs("/pnfs/data/mydir")
    is_online = client.namespace.is_online("/pnfs/data/file.dat")
    pnfs_id = client.namespace.get_pnfs_id("/pnfs/data/file.dat")

    # Recursive file listing
    all_files = client.namespace.with_files_in_dir("/pnfs/data/mydir", recursive=True)
```

Available services on `AdaClient`:

| Service | Attribute | Operations |
|---------|-----------|------------|
| Namespace | `client.namespace` | File/directory operations, path type, recursive traversal |
| Labels | `client.labels` | Label get/set/remove/find |
| Xattr | `client.xattr` | Extended attribute get/set/remove/find |
| Staging | `client.staging` | Stage, unstage, bulk requests |
| Checksums | `client.checksums` | Checksum retrieval |
| System | `client.system` | whoami, space, quota |
