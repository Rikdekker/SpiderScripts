"""CLI commands for namespace (file/directory) operations."""

from __future__ import annotations

import json

import click


@click.command("list")
@click.argument("path")
@click.pass_context
def list_cmd(ctx: click.Context, path: str) -> None:
    """List a directory."""
    from ada.cli.app import get_client

    with get_client(ctx) as client:
        for item in client.list(path):
            click.echo(item)


@click.command()
@click.argument("path", required=False)
@click.option("--from-file", "from_file", type=click.Path(exists=True), help="File containing paths to list")
@click.pass_context
def longlist(ctx: click.Context, path: str | None, from_file: str | None) -> None:
    """List file(s) or directory with details (size, date, QoS, locality)."""
    from ada.cli.app import get_client
    from ada.cli.formatters import format_longlist

    with get_client(ctx) as client:
        if from_file:
            paths = open(from_file).read().strip().splitlines()
        elif path:
            paths = [path]
        else:
            raise click.UsageError("Provide a PATH or --from-file.")
        results = client.longlist(paths)
        for line in format_longlist(results):
            click.echo(line)


@click.command("stat")
@click.argument("path")
@click.pass_context
def stat_cmd(ctx: click.Context, path: str) -> None:
    """Show all metadata of a file or directory."""
    from ada.cli.app import get_client

    with get_client(ctx) as client:
        info = client.stat(path)
        # Output key fields in a readable format
        click.echo(f"Path:       {info.path}")
        click.echo(f"Type:       {info.file_type.value}")
        if info.pnfs_id:
            click.echo(f"PNFS ID:    {info.pnfs_id}")
        if info.size is not None:
            click.echo(f"Size:       {info.size}")
        if info.mtime:
            click.echo(f"Modified:   {info.mtime.strftime('%Y-%m-%d %H:%M:%S UTC')}")
        if info.current_qos:
            qos = info.current_qos
            if info.target_qos:
                qos += f" -> {info.target_qos}"
            click.echo(f"QoS:        {qos}")
        if info.locality:
            click.echo(f"Locality:   {info.locality.value}")
        if info.labels:
            click.echo(f"Labels:     {', '.join(info.labels)}")
        if info.extended_attributes:
            click.echo(f"Xattr:      {json.dumps(info.extended_attributes)}")
        if info.checksums:
            for cs in info.checksums:
                click.echo(f"Checksum:   {cs.checksum_type}: {cs.value}")


@click.command()
@click.argument("path")
@click.option("--recursive", is_flag=True, help="Create parent directories as needed")
@click.pass_context
def mkdir(ctx: click.Context, path: str, recursive: bool) -> None:
    """Create a directory."""
    from ada.cli.app import get_client

    with get_client(ctx) as client:
        result = client.mkdir(path, recursive=recursive)
        click.echo(result)


@click.command()
@click.argument("source")
@click.argument("destination")
@click.pass_context
def mv(ctx: click.Context, source: str, destination: str) -> None:
    """Move or rename a file or directory."""
    from ada.cli.app import get_client

    with get_client(ctx) as client:
        result = client.mv(source, destination)
        click.echo(result)


@click.command()
@click.argument("path")
@click.option("--recursive", is_flag=True, help="Delete recursively")
@click.option("--force", is_flag=True, help="Skip confirmation prompt")
@click.pass_context
def delete(ctx: click.Context, path: str, recursive: bool, force: bool) -> None:
    """Delete a file or directory."""
    from ada.cli.app import get_client

    if not force and recursive:
        click.confirm(
            f"Are you sure you want to recursively delete '{path}' and all its contents?",
            abort=True,
        )

    with get_client(ctx) as client:
        client.delete(path, recursive=recursive, force=force)
        click.echo(f"Deleted: {path}")
