"""CLI commands for label management."""

from __future__ import annotations

import click


@click.command()
@click.argument("path")
@click.argument("label")
@click.pass_context
def setlabel(ctx: click.Context, path: str, label: str) -> None:
    """Attach a label to a file."""
    from ada.cli.app import get_client

    with get_client(ctx) as client:
        result = client.set_label(path, label)
        click.echo(result)


@click.command()
@click.argument("path")
@click.argument("label", required=False)
@click.pass_context
def lslabel(ctx: click.Context, path: str, label: str | None) -> None:
    """List labels of a file."""
    from ada.cli.app import get_client

    with get_client(ctx) as client:
        labels = client.list_labels(path, label=label)
        for lbl in labels:
            click.echo(lbl)


@click.command()
@click.argument("path")
@click.argument("label", required=False)
@click.option("--all", "remove_all", is_flag=True, help="Remove all labels")
@click.pass_context
def rmlabel(ctx: click.Context, path: str, label: str | None, remove_all: bool) -> None:
    """Remove a label from a file."""
    from ada.cli.app import get_client

    if not label and not remove_all:
        raise click.UsageError("Specify a LABEL or --all.")

    with get_client(ctx) as client:
        result = client.remove_label(path, label=label or "", all=remove_all)
        click.echo(result)


@click.command()
@click.argument("path")
@click.argument("regex")
@click.option("--recursive", is_flag=True, help="Search subdirectories")
@click.pass_context
def findlabel(ctx: click.Context, path: str, regex: str, recursive: bool) -> None:
    """Find files with labels matching a regex."""
    from ada.cli.app import get_client

    with get_client(ctx) as client:
        results = client.find_label(path, regex, recursive=recursive)
        for file_path, labels in results:
            click.echo(f"{file_path}\t{', '.join(labels)}")
