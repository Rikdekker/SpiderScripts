"""CLI commands for staging/unstaging (tape management)."""

from __future__ import annotations

import json

import click


@click.command()
@click.argument("path", required=False)
@click.option("--recursive", is_flag=True, help="Stage files recursively in directories")
@click.option("--lifetime", default="7D", help="Pin lifetime (e.g., 7D, 24H, 30M). Default: 7D")
@click.option("--from-file", "from_file", type=click.Path(exists=True), help="File containing paths to stage")
@click.pass_context
def stage(
    ctx: click.Context,
    path: str | None,
    recursive: bool,
    lifetime: str,
    from_file: str | None,
) -> None:
    """Bring files from tape to disk (stage/pin)."""
    from ada.cli.app import get_client

    if not path and not from_file:
        raise click.UsageError("Provide a PATH or --from-file.")

    with get_client(ctx) as client:
        result = client.stage(
            paths=path or [],
            recursive=recursive,
            lifetime=lifetime,
            from_file=from_file,
        )
        click.echo(f"Stage request submitted: {result.request_id}")
        if result.request_url:
            click.echo(f"Request URL: {result.request_url}")
        click.echo(f"Targets: {len(result.targets)} file(s)")


@click.command()
@click.argument("path", required=False)
@click.option("--recursive", is_flag=True, help="Unstage files recursively")
@click.option("--request-id", help="Specific bulk request ID to unpin")
@click.option("--from-file", "from_file", type=click.Path(exists=True), help="File containing paths")
@click.pass_context
def unstage(
    ctx: click.Context,
    path: str | None,
    recursive: bool,
    request_id: str | None,
    from_file: str | None,
) -> None:
    """Release disk copies so dCache can purge them (unstage/unpin)."""
    from ada.cli.app import get_client

    if not path and not from_file:
        raise click.UsageError("Provide a PATH or --from-file.")

    with get_client(ctx) as client:
        result = client.unstage(
            paths=path or [],
            recursive=recursive,
            request_id=request_id,
            from_file=from_file,
        )
        click.echo(f"Unstage request submitted: {result.request_id}")


@click.command("stat-request")
@click.argument("request_id")
@click.pass_context
def stat_request(ctx: click.Context, request_id: str) -> None:
    """Check the status of a bulk request."""
    from ada.cli.app import get_client

    with get_client(ctx) as client:
        status = client.stat_request(request_id)
        click.echo(f"Request: {status.uid}")
        click.echo(f"Status:  {status.status}")
        if status.targets:
            click.echo(f"Targets: {len(status.targets)}")
            for target in status.targets:
                if isinstance(target, dict):
                    t_path = target.get("target", target.get("path", "?"))
                    t_state = target.get("state", "?")
                    click.echo(f"  {t_path}: {t_state}")


@click.command("delete-request")
@click.argument("request_id")
@click.pass_context
def delete_request(ctx: click.Context, request_id: str) -> None:
    """Delete a bulk request."""
    from ada.cli.app import get_client

    with get_client(ctx) as client:
        client.delete_request(request_id)
        click.echo(f"Request {request_id} deleted.")
