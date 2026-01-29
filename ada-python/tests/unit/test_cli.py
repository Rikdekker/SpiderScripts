"""Tests for ada.cli module."""

from __future__ import annotations

from click.testing import CliRunner

from ada.cli.app import cli


class TestCLI:
    def test_version(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        assert "ada" in result.output.lower()

    def test_help(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "Advanced dCache API" in result.output

    def test_no_command_shows_help(self):
        runner = CliRunner()
        result = runner.invoke(cli, [])
        assert result.exit_code == 0
        assert "Usage" in result.output

    def test_list_subcommands_present(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])
        # Check key commands are registered
        for cmd in ["list", "longlist", "stat", "mkdir", "mv", "delete",
                     "stage", "unstage", "whoami", "viewtoken"]:
            assert cmd in result.output, f"Command '{cmd}' not found in help output"
