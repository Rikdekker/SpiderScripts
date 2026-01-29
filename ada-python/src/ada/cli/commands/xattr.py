"""CLI commands for extended attribute (xattr) management."""

from __future__ import annotations

import json
import sys

import click


@click.command()
@click.argument("path")
@click.argument("attribute_source", required=False)
@click.option("--stdin", "from_stdin", is_flag=True, help="Read attributes from stdin")
@click.pass_context
def setxattr(
    ctx: click.Context, path: str, attribute_source: str | None, from_stdin: bool
) -> None:
    """Set extended attributes on a file.

    ATTRIBUTE_SOURCE can be a file path or a JSON/key=value string.
    Use --stdin to read from standard input.
    """
    from ada.cli.app import get_client

    if from_stdin or attribute_source == "-":
        content = sys.stdin.read().strip()
    elif attribute_source:
        from pathlib import Path

        p = Path(attribute_source)
        if p.is_file():
            content = p.read_text().strip()
        else:
            content = attribute_source
    else:
        raise click.UsageError("Provide an ATTRIBUTE_SOURCE, file path, or --stdin.")

    with get_client(ctx) as client:
        result = client.set_xattr(path, content)
        click.echo(result)


@click.command()
@click.argument("path")
@click.argument("key", required=False)
@click.pass_context
def lsxattr(ctx: click.Context, path: str, key: str | None) -> None:
    """List extended attributes of a file."""
    from ada.cli.app import get_client

    with get_client(ctx) as client:
        xattrs = client.list_xattr(path, key=key)
        if xattrs:
            click.echo(json.dumps(xattrs, indent=2))
        else:
            click.echo("No extended attributes found.")


@click.command()
@click.argument("path")
@click.argument("key", required=False)
@click.option("--all", "remove_all", is_flag=True, help="Remove all attributes")
@click.pass_context
def rmxattr(ctx: click.Context, path: str, key: str | None, remove_all: bool) -> None:
    """Remove extended attribute(s) from a file."""
    from ada.cli.app import get_client

    if not key and not remove_all:
        raise click.UsageError("Specify a KEY or --all.")

    with get_client(ctx) as client:
        result = client.remove_xattr(path, key=key or "", all=remove_all)
        click.echo(result)


@click.command()
@click.argument("path")
@click.argument("key")
@click.argument("regex")
@click.option("--recursive", is_flag=True, help="Search subdirectories")
@click.option("--all", "all_keys", is_flag=True, help="Search all attribute keys")
@click.pass_context
def findxattr(
    ctx: click.Context, path: str, key: str, regex: str, recursive: bool, all_keys: bool
) -> None:
    """Find files with extended attributes matching a regex."""
    from ada.cli.app import get_client

    with get_client(ctx) as client:
        results = client.find_xattr(
            path, key=key, regex=regex, recursive=recursive, all_keys=all_keys
        )
        for file_path, attrs in results:
            click.echo(f"{file_path}\t{json.dumps(attrs)}")
