"""Dispatch the pinned fabrication tools without owning a design project."""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from importlib.metadata import version
from pathlib import Path


TOOLS = ("cadkit", "fitkit", "prusa-cli-preview")


def _command(name: str) -> Path:
    """An entry-point script in this Toolbox environment."""
    return Path(sys.executable).parent / name


def _run(command: list[str], env: dict[str, str] | None = None) -> int:
    return subprocess.run(command, check=False, env=env).returncode


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
        ("python", "run Python from the pinned CAD environment"),
    ):
        # The wrapped command owns all of its options, including --help.
        commands.add_parser(name, help=help_text, add_help=False)
    preview = commands.add_parser(
        "preview",
        help="open a ready viewer, then run a project preview command",
    )
    preview.add_argument("--port", type=int, default=None,
                         help="explicit isolated viewer port")
    preview.add_argument("--name", default=None,
                         help="viewer ownership label")
    preview.add_argument("--wait", type=float, default=25.0,
                         help="seconds to wait for the browser (default: 25)")
    preview.add_argument("preview_command", nargs=argparse.REMAINDER,
                         metavar="COMMAND",
                         help="command to run after the browser is ready; prefix it with --")
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
    if args.command == "python":
        raise SystemExit(_run([sys.executable, *tool_args]))
    if args.command == "preview":
        command = args.preview_command
        if command[:1] == ["--"]:
            command = command[1:]
        if not command:
            command_parser.error("preview requires a command after --")
        from cadkit import viewer

        try:
            port, _ = viewer.prepare(port=args.port, name=args.name, wait=args.wait)
        except RuntimeError as exc:
            print(f"preview: {exc}", file=sys.stderr)
            raise SystemExit(2) from exc
        env = os.environ.copy()
        env["CAD_VIEWER_PORT"] = str(port)
        raise SystemExit(_run(command, env=env))
