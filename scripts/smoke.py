"""Install a distribution in a new venv, then run it outside the checkout.

Uses only the standard library so the matrix does not need the CI toolchain.
"""

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import venv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(command, *, cwd, env):
    print("+", " ".join(map(str, command)), flush=True)
    return subprocess.run(
        list(map(str, command)), cwd=cwd, env=env, check=True, capture_output=True, text=True
    ).stdout


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("distribution", type=Path)
    parser.add_argument(
        "--cold", action="store_true", help="Resolve from wheel metadata, no preinstall"
    )
    args = parser.parse_args()
    distribution = args.distribution.resolve()
    clean_env = os.environ.copy()
    clean_env.pop("PYTHONPATH", None)
    clean_env.pop("PYTHONHOME", None)
    clean_env["PYTHONNOUSERSITE"] = "1"
    with tempfile.TemporaryDirectory(prefix="gpu-budget-consumer-") as temporary:
        work = Path(temporary)
        environment = work / "env"
        venv.EnvBuilder(with_pip=True).create(environment)
        binaries = environment / ("Scripts" if os.name == "nt" else "bin")
        python = binaries / ("python.exe" if os.name == "nt" else "python")
        executable = binaries / ("gpu-budget.exe" if os.name == "nt" else "gpu-budget")
        if args.cold:
            install = [
                python,
                "-m",
                "pip",
                "install",
                "--no-cache-dir",
                "--constraint",
                ROOT / "requirements/runtime.in",
                distribution,
            ]
        else:
            # Resolve the artifact and the locked dependencies in one transaction.
            # No editable install, source tree, existing venv, or pip cache.
            digest = hashlib.sha256(distribution.read_bytes()).hexdigest()
            requirement = work / "artifact.txt"
            requirement.write_text(
                f"{distribution.as_uri()} --hash=sha256:{digest}\n", encoding="utf-8"
            )
            install = [
                python,
                "-m",
                "pip",
                "install",
                "--no-cache-dir",
                "--require-hashes",
                "-r",
                ROOT / "requirements/runtime.lock",
                "-r",
                requirement,
            ]
        print(run(install, cwd=work, env=clean_env))
        print(run([python, "-m", "pip", "check"], cwd=work, env=clean_env))
        location = run(
            [python, "-I", "-c", "import gpu_budget; print(gpu_budget.__file__)"],
            cwd=work,
            env=clean_env,
        ).strip()
        assert environment.resolve() in Path(location).resolve().parents, location
        print("Imported installed package:", location)
        output = run([executable], cwd=work, env=clean_env)
        result = json.loads(output)
        assert result["monthly_usd"] == "4.27", output
        assert result["retry_ceiling_usd"] == "8.54", output
        # Also exercise an explicit plan path containing spaces.
        custom = work / "my plan.toml"
        custom.write_text(
            (ROOT / "src/gpu_budget/profiles/demo.toml")
            .read_text(encoding="utf-8")
            .replace('usd_per_hour = "0.44"', 'usd_per_hour = "0.88"'),
            encoding="utf-8",
        )
        output = run([executable, "--plan", custom], cwd=work, env=clean_env)
        assert json.loads(output)["monthly_usd"] == "8.54", output
        broken = work / "bad.toml"
        broken.write_text('[billing]\nusd_per_hour = "NaN"\n', encoding="utf-8")
        error = subprocess.run(
            [str(executable), "--plan", str(broken)],
            cwd=work,
            env=clean_env,
            capture_output=True,
            text=True,
        )
        assert error.returncode == 2, error
        assert "Invalid plan:" in error.stderr, error.stderr
        print("Installed CLI, bundled data, spaced path and invalid input: OK")


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as exc:
        print(exc.stdout or "", file=sys.stderr)
        print(exc.stderr or "", file=sys.stderr)
        raise
