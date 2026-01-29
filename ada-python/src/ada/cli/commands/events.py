"""CLI commands for SSE event streaming and channel management."""

from __future__ import annotations

import json

import click


@click.command("events")
@click.argument("channel_name")
@click.argument("path")
@click.option("--recursive", is_flag=True, help="Subscribe to events recursively")
@click.option("--resume", is_flag=True, help="Resume from last processed event")
@click.option("--force", is_flag=True, help="Force create channel even if it exists")
@click.option("--timeout", default=3600, type=int, help="Connection timeout in seconds (default: 3600)")
@click.pass_context
def events_cmd(
    ctx: click.Context,
    channel_name: str,
    path: str,
    recursive: bool,
    resume: bool,
    force: bool,
    timeout: int,
) -> None:
    """Subscribe to inotify events on a path via SSE.

    Events are printed as JSON, one per line.
    """
    from ada.cli.app import get_client

    with get_client(ctx) as client:
        events_service = client._api  # Access low-level API for SSE
        # This is handled by the events service
        from ada.services.events import EventService

        svc = EventService(client._api)
        for event in svc.subscribe(
            channel_name=channel_name,
            path=path,
            recursive=recursive,
            resume=resume,
            force=force,
            timeout=timeout,
        ):
            click.echo(json.dumps(event, default=str))


@click.command("report-staged")
@click.argument("channel_name")
@click.argument("path")
@click.option("--recursive", is_flag=True, help="Monitor recursively")
@click.pass_context
def report_staged(
    ctx: click.Context, channel_name: str, path: str, recursive: bool
) -> None:
    """Monitor file locality/QoS changes (staging progress)."""
    from ada.cli.app import get_client

    with get_client(ctx) as client:
        from ada.services.events import EventService

        svc = EventService(client._api)
        for event in svc.report_staged(
            channel_name=channel_name, path=path, recursive=recursive
        ):
            click.echo(json.dumps(event, default=str))


@click.command()
@click.argument("name", required=False)
@click.pass_context
def channels(ctx: click.Context, name: str | None) -> None:
    """List existing event channels and subscriptions."""
    from ada.cli.app import get_client

    with get_client(ctx) as client:
        from ada.services.events import EventService

        svc = EventService(client._api)
        result = svc.list_channels(name=name)
        if isinstance(result, list):
            for ch in result:
                click.echo(json.dumps(ch, default=str))
        elif result:
            click.echo(json.dumps(result, default=str))
        else:
            click.echo("No channels found.")


@click.command("delete-channel")
@click.argument("name")
@click.pass_context
def delete_channel(ctx: click.Context, name: str) -> None:
    """Delete an event channel."""
    from ada.cli.app import get_client

    with get_client(ctx) as client:
        from ada.services.events import EventService

        svc = EventService(client._api)
        svc.delete_channel(name)
        click.echo(f"Channel '{name}' deleted.")
