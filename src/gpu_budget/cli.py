"""Keep the CLI runnable from an installed wheel on Linux and Windows."""

import argparse
import json
import os
import pwd
import sys
from decimal import Decimal
from importlib.resources import files
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # Python 3.10
    import tomli as tomllib

from gpu_budget import __version__
from gpu_budget.budget import estimate


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Estimate monthly GPU CI compute spend.",
        epilog=f"Budget owner: {pwd.getpwuid(os.getuid()).pw_name}",
    )
    parser.add_argument("--version", action="version", version=__version__)
    parser.add_argument("--plan", type=Path, help="TOML plan; defaults to the bundled example")
    args = parser.parse_args(argv)
    try:
        text = (
            args.plan.read_text(encoding="utf-8")
            if args.plan
            else files("gpu_budget").joinpath("profiles/demo.toml").read_text(encoding="utf-8")
        )
        result = estimate(tomllib.loads(text, parse_float=Decimal))
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"Invalid plan: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
