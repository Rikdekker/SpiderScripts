"""CLI command for checksum retrieval."""

from __future__ import annotations

import click


@click.command("checksum")
@click.argument("path", required=False)
@click.option("--recursive", is_flag=True, help="Get checksums recursively")
@click.option("--from-file", "from_file", type=click.Path(exists=True), help="File containing paths")
@click.pass_context
def checksum_cmd(ctx: click.Context, path: str | None, recursive: bool, from_file: str | None) -> None:
    """Get MD5/Adler32 checksums for file(s)."""
    from ada.cli.app import get_client

    if not path and not from_file:
        raise click.UsageError("Provide a PATH or --from-file.")

    with get_client(ctx) as client:
        checksums = client.checksum(
            paths=path or [],
            recursive=recursive,
            from_file=from_file,
        )
        for cs in checksums:
            click.echo(f"{cs.value}  {cs.path}  ({cs.checksum_type})")
