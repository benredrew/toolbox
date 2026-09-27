"""Dispatch the pinned fabrication tools without owning a design project."""
from __future__ import annotations

import argparse
import subprocess
import sys
from importlib.metadata import version
from pathlib import Path


TOOLS = ("cadkit", "fitkit", "prusa-cli-preview")


def _command(name: str) -> Path:
    """An entry-point script in this Toolbox environment."""
    return Path(sys.executable).parent / name


def _run(command: list[str]) -> int:
    return subprocess.run(command, check=False).returncode


def doctor() -> int:
    """Check the installed toolchain and its external slicer prerequisites."""
    healthy = True
    for package in TOOLS:
        try:
            print(f"{package}: {version(package)}")
        except Exception as exc:
            healthy = False
            print(f"{package}: unavailable ({exc})", file=sys.stderr)

    if healthy:
        try:
            import cadquery  # noqa: F401
            import ocp_vscode  # noqa: F401
        except Exception as exc:
            healthy = False
            print(f"CAD runtime: unavailable ({exc})", file=sys.stderr)
        else:
            print("CAD runtime: ready")

    print("PrusaSlicer prerequisites:")
    result = _run([str(_command("slice-with-preview")), "--doctor"])
    return 0 if healthy and result == 0 else 2


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(
        prog="toolbox",
        description="Pinned CAD and fabrication tools, independent of any design project.",
    )
    commands = result.add_subparsers(dest="command", required=True)
    commands.add_parser("doctor", help="check the full local toolchain")
    for name, help_text in (
        ("fit", "run Fitkit (for example: fit cylinder 112)"),
        ("slice", "run Slice With Preview"),
        ("viewer", "run CadKit's viewer command"),
    ):
        # The wrapped command owns all of its options, including --help.
        commands.add_parser(name, help=help_text, add_help=False)
    return result


def main(argv: list[str] | None = None) -> None:
    command_parser = parser()
    args, tool_args = command_parser.parse_known_args(argv)
    if args.command == "doctor":
        if tool_args:
            command_parser.error("doctor does not accept arguments")
        raise SystemExit(doctor())
    if args.command == "fit":
        raise SystemExit(_run([str(_command("fit-test")), *tool_args]))
    if args.command == "slice":
        raise SystemExit(_run([str(_command("slice-with-preview")), *tool_args]))
    if args.command == "viewer":
        raise SystemExit(_run([sys.executable, "-m", "cadkit.viewer", *tool_args]))
