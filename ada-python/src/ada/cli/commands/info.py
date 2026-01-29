"""CLI commands for system information (whoami, space, quota, viewtoken)."""

from __future__ import annotations

import json

import click


@click.command()
@click.pass_context
def whoami(ctx: click.Context) -> None:
    """Show the authenticated user's identity."""
    from ada.cli.app import get_client

    with get_client(ctx) as client:
        info = client.whoami()
        click.echo(f"Status:   {info.status}")
        if info.username:
            click.echo(f"Username: {info.username}")
        if info.uid is not None:
            click.echo(f"UID:      {info.uid}")
        if info.gids:
            click.echo(f"GIDs:     {', '.join(str(g) for g in info.gids)}")
        if info.home:
            click.echo(f"Home:     {info.home}")
        if info.root:
            click.echo(f"Root:     {info.root}")
        # Show dCache version if available
        raw = info.raw
        if "version" in raw:
            click.echo(f"dCache:   {raw['version']}")


@click.command()
@click.pass_context
def viewtoken(ctx: click.Context) -> None:
    """Display token properties (decode JWT/OIDC or Macaroon)."""
    from ada.cli.app import get_client

    with get_client(ctx) as client:
        token_info = client.view_token()
        click.echo(json.dumps(token_info, indent=2))


@click.command()
@click.argument("poolgroup", required=False)
@click.pass_context
def space(ctx: click.Context, poolgroup: str | None) -> None:
    """Show storage space in pool groups.

    Without POOLGROUP, lists all available pool groups.
    With POOLGROUP, shows space details.
    """
    from ada.cli.app import get_client
    from ada.models import SpaceInfo
    from ada.utils import human_readable_size

    with get_client(ctx) as client:
        result = client.space(poolgroup)
        if isinstance(result, SpaceInfo):
            click.echo(f"Total:     {human_readable_size(result.total)}")
            click.echo(f"Free:      {human_readable_size(result.free)}")
            click.echo(f"Precious:  {human_readable_size(result.precious)}")
            click.echo(f"Removable: {human_readable_size(result.removable)}")
        elif isinstance(result, list):
            for name in result:
                click.echo(name)


@click.command()
@click.pass_context
def quota(ctx: click.Context) -> None:
    """Display storage quotas (disk & tape)."""
    from ada.cli.app import get_client
    from ada.utils import human_readable_size

    with get_client(ctx) as client:
        quotas = client.quota()
        if not quotas:
            click.echo("No quota information available.")
            return
        for q in quotas:
            click.echo(f"Type: {q.quota_type} (ID: {q.id})")
            custodial_limit = (
                human_readable_size(q.custodial_limit)
                if q.custodial_limit
                else "unlimited"
            )
            replica_limit = (
                human_readable_size(q.replica_limit)
                if q.replica_limit
                else "unlimited"
            )
            click.echo(f"  Tape:  {human_readable_size(q.custodial)} / {custodial_limit}")
            click.echo(f"  Disk:  {human_readable_size(q.replica)} / {replica_limit}")
