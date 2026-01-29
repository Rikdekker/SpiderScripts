# CLI Reference

## Global Options

These options apply to all commands and must be placed before the subcommand:

```bash
ada [GLOBAL OPTIONS] COMMAND [COMMAND OPTIONS] [ARGUMENTS]
```

| Option | Env Variable | Description |
|--------|-------------|-------------|
| `--api URL` | `ada_api` | dCache API URL (e.g., `https://host/api/v1`) |
| `--tokenfile PATH` | `ada_tokenfile` | Path to bearer token file |
| `--token TOKEN` | `BEARER_TOKEN` | Bearer token string (direct) |
| `--netrc [PATH]` | `ada_netrcfile` | Use netrc file (default: `~/.netrc`) |
| `--proxy [PATH]` | — | Use X.509 proxy certificate |
| `--debug / --no-debug` | `ada_debug` | Enable debug output |
| `--igtf / --no-igtf` | — | Use IGTF Grid certificates (default: on) |
| `--version` | — | Show version and exit |
| `--help` | — | Show help and exit |

## File & Directory Operations

### `list`

List directory contents.

```bash
ada list /pnfs/data/mydir
```

Output shows file names, with directories suffixed by `/`.

### `longlist`

List with details (size, date, QoS, locality).

```bash
ada longlist /pnfs/data/mydir
ada longlist --from-file paths.txt
```

| Option | Description |
|--------|-------------|
| `--from-file PATH` | File containing paths (one per line) |

### `stat`

Show all metadata for a file or directory.

```bash
ada stat /pnfs/data/mydir/file.dat
```

Output includes: path, type, PNFS ID, size, modification time, QoS, locality, labels, extended attributes, and checksums.

### `mkdir`

Create a directory.

```bash
ada mkdir /pnfs/data/mydir/newdir
ada mkdir /pnfs/data/mydir/a/b/c --recursive
```

| Option | Description |
|--------|-------------|
| `--recursive` | Create parent directories as needed (max 10 levels) |

### `mv`

Move or rename a file or directory.

```bash
ada mv /pnfs/data/oldname /pnfs/data/newname
```

### `delete`

Delete a file or directory.

```bash
ada delete /pnfs/data/file.dat
ada delete /pnfs/data/mydir --recursive --force
```

| Option | Description |
|--------|-------------|
| `--recursive` | Delete directory contents recursively |
| `--force` | Skip confirmation prompt |

## Label Operations

Labels are simple string tags attached to files (not directories).

### `setlabel`

Attach a label to a file.

```bash
ada setlabel /pnfs/data/file.dat important
```

### `lslabel`

List labels on a file.

```bash
ada lslabel /pnfs/data/file.dat
ada lslabel /pnfs/data/file.dat important    # Check specific label
```

### `rmlabel`

Remove a label.

```bash
ada rmlabel /pnfs/data/file.dat important
ada rmlabel /pnfs/data/file.dat --all
```

| Option | Description |
|--------|-------------|
| `--all` | Remove all labels |

### `findlabel`

Find files with labels matching a regex.

```bash
ada findlabel /pnfs/data/mydir "import.*"
ada findlabel /pnfs/data/mydir "batch-[0-9]+" --recursive
```

| Option | Description |
|--------|-------------|
| `--recursive` | Search subdirectories |

## Extended Attribute Operations

Extended attributes are key-value metadata pairs on files.

### `setxattr`

Set extended attributes.

```bash
# From a JSON string
ada setxattr /pnfs/data/file.dat '{"project": "spider", "batch": "42"}'

# From a file
ada setxattr /pnfs/data/file.dat attributes.json

# From key=value format
ada setxattr /pnfs/data/file.dat "project=spider,batch=42"

# From stdin
echo '{"project": "spider"}' | ada setxattr /pnfs/data/file.dat --stdin
```

| Option | Description |
|--------|-------------|
| `--stdin` | Read attributes from standard input |

### `lsxattr`

List extended attributes.

```bash
ada lsxattr /pnfs/data/file.dat
ada lsxattr /pnfs/data/file.dat project    # Specific key
```

### `rmxattr`

Remove extended attributes.

```bash
ada rmxattr /pnfs/data/file.dat project
ada rmxattr /pnfs/data/file.dat --all
```

| Option | Description |
|--------|-------------|
| `--all` | Remove all attributes |

### `findxattr`

Find files with attributes matching a regex.

```bash
ada findxattr /pnfs/data/mydir project "spider.*"
ada findxattr /pnfs/data/mydir project "spider" --recursive
```

| Option | Description |
|--------|-------------|
| `--recursive` | Search subdirectories |
| `--all` | Search all attribute keys |

## Staging Operations (Tape Management)

### `stage`

Bring files from tape to disk.

```bash
ada stage /pnfs/data/file.dat
ada stage /pnfs/data/file.dat --lifetime 14D
ada stage /pnfs/data/mydir --recursive
ada stage --from-file filelist.txt --lifetime 7D
```

| Option | Description |
|--------|-------------|
| `--lifetime DURATION` | Pin lifetime (default: `7D`). Format: `<number><unit>` where unit is `S`/`M`/`H`/`D` |
| `--recursive` | Stage files in subdirectories |
| `--from-file PATH` | File containing paths (one per line) |

### `unstage`

Release disk copies so dCache can purge them.

```bash
ada unstage /pnfs/data/file.dat
ada unstage /pnfs/data/mydir --recursive
ada unstage --from-file filelist.txt
ada unstage /pnfs/data/file.dat --request-id abc-123
```

| Option | Description |
|--------|-------------|
| `--recursive` | Unstage recursively |
| `--request-id ID` | Specific bulk request to unpin |
| `--from-file PATH` | File containing paths |

### `stat-request`

Check the status of a bulk staging/unstaging request.

```bash
ada stat-request abc-123-def-456
```

### `delete-request`

Delete a bulk request.

```bash
ada delete-request abc-123-def-456
```

## Checksum Operations

### `checksum`

Get MD5 and Adler32 checksums.

```bash
ada checksum /pnfs/data/file.dat
ada checksum /pnfs/data/mydir --recursive
ada checksum --from-file filelist.txt
```

| Option | Description |
|--------|-------------|
| `--recursive` | Get checksums for all files in subdirectories |
| `--from-file PATH` | File containing paths |

## Event Streaming (SSE)

### `events`

Subscribe to inotify events on a path via Server-Sent Events.

```bash
ada events mychannel /pnfs/data/mydir
ada events mychannel /pnfs/data/mydir --recursive --timeout 7200
ada events mychannel /pnfs/data/mydir --resume
```

| Option | Description |
|--------|-------------|
| `--recursive` | Watch subdirectories |
| `--resume` | Resume from last processed event |
| `--force` | Force create new channel |
| `--timeout SECONDS` | Connection timeout (default: 3600) |

Events are output as JSON, one per line.

### `report-staged`

Monitor file locality/QoS changes (staging progress).

```bash
ada report-staged mychannel /pnfs/data/mydir --recursive
```

### `channels`

List event channels.

```bash
ada channels
ada channels mychannel
```

### `delete-channel`

Delete an event channel.

```bash
ada delete-channel mychannel
```

## System Information

### `whoami`

Show the authenticated user's identity and dCache version.

```bash
ada whoami
```

### `viewtoken`

Decode and display token properties (JWT/OIDC or Macaroon).

```bash
ada viewtoken
```

### `space`

Show storage space in pool groups.

```bash
ada space                    # List all pool groups
ada space my-pool-group      # Show space details
```

### `quota`

Show storage quotas (disk and tape).

```bash
ada quota
```

## Command Mapping from Bash

If you are migrating from the Bash version of ADA, here is how commands translate:

| Bash (old) | Python (new) |
|---|---|
| `ada --list /path` | `ada list /path` |
| `ada --longlist /path` | `ada longlist /path` |
| `ada --stat /path` | `ada stat /path` |
| `ada --mkdir /path --recursive` | `ada mkdir /path --recursive` |
| `ada --mv /src /dst` | `ada mv /src /dst` |
| `ada --delete /path --recursive --force` | `ada delete /path --recursive --force` |
| `ada --setlabel /path label` | `ada setlabel /path label` |
| `ada --rmlabel /path label` | `ada rmlabel /path label` |
| `ada --lslabel /path` | `ada lslabel /path` |
| `ada --findlabel /dir regex` | `ada findlabel /dir regex` |
| `ada --setxattr /path file` | `ada setxattr /path file` |
| `ada --rmxattr /path key` | `ada rmxattr /path key` |
| `ada --lsxattr /path` | `ada lsxattr /path` |
| `ada --findxattr /dir key regex` | `ada findxattr /dir key regex` |
| `ada --checksum /path` | `ada checksum /path` |
| `ada --stage /path --lifetime 7D` | `ada stage /path --lifetime 7D` |
| `ada --unstage /path` | `ada unstage /path` |
| `ada --stat-request id` | `ada stat-request id` |
| `ada --delete-request id` | `ada delete-request id` |
| `ada --events chan /path` | `ada events chan /path` |
| `ada --report-staged chan /path` | `ada report-staged chan /path` |
| `ada --channels` | `ada channels` |
| `ada --delete-channel name` | `ada delete-channel name` |
| `ada --whoami` | `ada whoami` |
| `ada --viewtoken` | `ada viewtoken` |
| `ada --space` | `ada space` |
| `ada --quota` | `ada quota` |
