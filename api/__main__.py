# -*- coding: utf-8 -*-
# ruff: noqa: D401
"""Entry point."""
import click

from . import __version__, scripts


def _main() -> None:
    """Run main function for entrypoint."""

    @click.group(chain=True)
    @click.version_option(__version__)
    def entry_point() -> None:
        """Alexion test command line application."""

    entry_point.add_command(
        scripts.prepare_data,
    )

    entry_point()


if __name__ == "__main__":
    _main()
