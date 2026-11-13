"""Try three quiet failures against a real built artifact, without changing it."""

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def verify(directory, env):
    return subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/artifacts.py"),
            "verify",
            "--directory",
            str(directory),
        ],
        env=env,
        capture_output=True,
        text=True,
    )


def main():
    with tempfile.TemporaryDirectory(prefix="artifact-probes-") as temporary:
        root = Path(temporary)
        original = ROOT / "release"
        baseline = verify(original, os.environ.copy())
        if baseline.returncode:
            raise RuntimeError(baseline.stdout + baseline.stderr)
        for name in ("changed-bytes", "stale-commit", "wrong-tag"):
            candidate = root / name
            shutil.copytree(original, candidate)
            env = os.environ.copy()
            expected = "Artifact provenance mismatch"
            if name == "changed-bytes":
                # ZIP permits trailing bytes: metadata stays valid, digest changes.
                wheel = next((candidate / "dist").glob("*.whl"))
                with wheel.open("ab") as stream:
                    stream.write(b"not-the-tested-bytes")
            elif name == "stale-commit":
                record = candidate / "record.json"
                data = json.loads(record.read_text(encoding="utf-8"))
                data["commit"] = "a-different-commit"
                record.write_text(json.dumps(data), encoding="utf-8")
            else:
                env["GITHUB_REF"] = "refs/tags/v99.0.0"
                expected = "artifact version"
            result = verify(candidate, env)
            if result.returncode == 0 or expected not in result.stderr:
                raise RuntimeError(f"{name}: wrong outcome\n{result.stdout}\n{result.stderr}")
            print(f"BLOCKED {name}: {result.stderr.strip().splitlines()[-1]}")


if __name__ == "__main__":
    main()
