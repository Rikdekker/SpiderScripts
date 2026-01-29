"""CLI entry point for ADA.

Uses Click to provide a command-line interface that maps subcommands
to AdaClient methods. Global options (auth, API URL, debug) are
shared across all commands.
"""

from __future__ import annotations

import logging
import sys
from typing import Optional

import click

from ada import __version__
from ada.exceptions import AdaError


class AliasedGroup(click.Group):
    """Click group that supports command aliases via prefix matching."""

    def get_command(self, ctx: click.Context, cmd_name: str) -> Optional[click.Command]:
        rv = click.Group.get_command(self, ctx, cmd_name)
        if rv is not None:
            return rv
        # Allow prefix matching for convenience
        matches = [x for x in self.list_commands(ctx) if x.startswith(cmd_name)]
        if not matches:
            return None
        if len(matches) == 1:
            return click.Group.get_command(self, ctx, matches[0])
        ctx.fail(f"Ambiguous command '{cmd_name}'. Could be: {', '.join(sorted(matches))}")
        return None


@click.group(cls=AliasedGroup, invoke_without_command=True)
@click.option("--api", envvar="ada_api", help="dCache API URL (e.g., https://host/api/v1)")
@click.option("--tokenfile", envvar="ada_tokenfile", help="Path to token file")
@click.option("--token", envvar="BEARER_TOKEN", help="Bearer token string")
@click.option(
    "--netrc",
    "netrcfile",
    is_flag=False,
    flag_value="~/.netrc",
    default=None,
    help="Use netrc file for authentication",
)
@click.option(
    "--proxy",
    "proxyfile",
    is_flag=False,
    flag_value="auto",
    default=None,
    help="Use X.509 proxy certificate",
)
@click.option("--debug/--no-debug", envvar="ada_debug", default=False, help="Enable debug output")
@click.option(
    "--igtf/--no-igtf",
    default=True,
    help="Use IGTF Grid certificates (default: true)",
)
@click.version_option(__version__, "--version", prog_name="ada")
@click.pass_context
def cli(
    ctx: click.Context,
    api: Optional[str],
    tokenfile: Optional[str],
    token: Optional[str],
    netrcfile: Optional[str],
    proxyfile: Optional[str],
    debug: bool,
    igtf: bool,
) -> None:
    """ADA - Advanced dCache API tool to manage your data in dCache."""
    if debug:
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(name)s: %(message)s",
            stream=sys.stderr,
        )

    ctx.ensure_object(dict)
    ctx.obj["api"] = api
    ctx.obj["tokenfile"] = tokenfile
    ctx.obj["token"] = token
    ctx.obj["netrcfile"] = netrcfile
    ctx.obj["proxyfile"] = proxyfile
    ctx.obj["debug"] = debug
    ctx.obj["igtf"] = igtf

    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


def get_client(ctx: click.Context):
    """Create an AdaClient from the CLI context."""
    from ada.core.client import AdaClient

    obj = ctx.obj
    proxy = obj.get("proxyfile")
    if proxy == "auto":
        proxy = ""  # Let ProxyAuth use default path

    return AdaClient(
        api=obj.get("api"),
        tokenfile=obj.get("tokenfile"),
        token=obj.get("token"),
        netrc=obj.get("netrcfile"),
        proxy=proxy,
        debug=obj.get("debug", False),
        igtf=obj.get("igtf", True),
    )


# ---- Register all commands ----

from ada.cli.commands.namespace import (  # noqa: E402
    delete,
    list_cmd,
    longlist,
    mkdir,
    mv,
    stat_cmd,
)
from ada.cli.commands.labels import findlabel, lslabel, rmlabel, setlabel  # noqa: E402
from ada.cli.commands.xattr import findxattr, lsxattr, rmxattr, setxattr  # noqa: E402
from ada.cli.commands.staging import (  # noqa: E402
    delete_request,
    stage,
    stat_request,
    unstage,
)
from ada.cli.commands.events import (  # noqa: E402
    channels,
    delete_channel,
    events_cmd,
    report_staged,
)
from ada.cli.commands.info import quota, space, viewtoken, whoami  # noqa: E402
from ada.cli.commands.checksum import checksum_cmd  # noqa: E402

cli.add_command(list_cmd, "list")
cli.add_command(longlist, "longlist")
cli.add_command(stat_cmd, "stat")
cli.add_command(mkdir, "mkdir")
cli.add_command(mv, "mv")
cli.add_command(delete, "delete")
cli.add_command(setlabel, "setlabel")
cli.add_command(rmlabel, "rmlabel")
cli.add_command(lslabel, "lslabel")
cli.add_command(findlabel, "findlabel")
cli.add_command(setxattr, "setxattr")
cli.add_command(rmxattr, "rmxattr")
cli.add_command(lsxattr, "lsxattr")
cli.add_command(findxattr, "findxattr")
cli.add_command(stage, "stage")
cli.add_command(unstage, "unstage")
cli.add_command(stat_request, "stat-request")
cli.add_command(delete_request, "delete-request")
cli.add_command(events_cmd, "events")
cli.add_command(report_staged, "report-staged")
cli.add_command(channels, "channels")
cli.add_command(delete_channel, "delete-channel")
cli.add_command(whoami, "whoami")
cli.add_command(viewtoken, "viewtoken")
cli.add_command(space, "space")
cli.add_command(quota, "quota")
cli.add_command(checksum_cmd, "checksum")


def main() -> None:
    """Entry point for the CLI."""
    try:
        cli(standalone_mode=False)
    except click.exceptions.Abort:
        sys.exit(130)
    except click.ClickException as e:
        e.show()
        sys.exit(e.exit_code)
    except AdaError as e:
        click.echo(f"ERROR: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"ERROR: Unexpected error: {e}", err=True)
        sys.exit(1)
