"""Bind the build outputs to the current commit, and validate release metadata."""

import argparse
import hashlib
import json
import os
import re
import tarfile
import zipfile
from email.parser import BytesParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "release"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def distributions():
    paths = sorted((OUTPUT / "dist").glob("*"))
    require(len(paths) == 2, f"Expected exactly a wheel and sdist, got {paths}")
    require(sum(path.suffix == ".whl" for path in paths) == 1, "Expected one wheel")
    require(sum(path.name.endswith(".tar.gz") for path in paths) == 1, "Expected one sdist")
    return paths


def metadata(path):
    if path.suffix == ".whl":
        with zipfile.ZipFile(path) as archive:
            names = [name for name in archive.namelist() if name.endswith(".dist-info/METADATA")]
            require(len(names) == 1, "Expected one wheel metadata file")
            raw = archive.read(names[0])
    else:
        with tarfile.open(path) as archive:
            names = [
                name
                for name in archive.getnames()
                if name.count("/") == 1 and name.endswith("/PKG-INFO")
            ]
            require(len(names) == 1, "Expected one sdist metadata file")
            raw = archive.extractfile(names[0]).read()
    return BytesParser().parsebytes(raw)


def inspect():
    paths = distributions()
    versions = set()
    for path in paths:
        info = metadata(path)
        require(info["Name"] == "soup-gpu-budget-kreichik", f"Wrong package: {info['Name']}")
        require(info["Requires-Python"] == ">=3.10", "Wrong Python requirement")
        versions.add(info["Version"])
    require(len(versions) == 1, f"Wheel/sdist versions differ: {versions}")
    version = versions.pop()
    require(re.fullmatch(r"\d+\.\d+\.\d+", version), f"Invalid release version: {version}")
    ref = os.environ.get("GITHUB_REF", "local")
    if ref.startswith("refs/tags/"):
        require(ref == f"refs/tags/v{version}", f"Tag {ref} != artifact version {version}")
    return {
        "commit": os.environ.get("GITHUB_SHA", "local"),
        "ref": ref,
        "version": version,
        "sha256": {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in paths},
    }


def main():
    global OUTPUT
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["record", "verify"])
    parser.add_argument("--directory", type=Path, default=OUTPUT)
    args = parser.parse_args()
    OUTPUT = args.directory.resolve()
    observed = inspect()
    record = OUTPUT / "record.json"
    if args.mode == "record":
        record.write_text(json.dumps(observed, indent=2) + "\n", encoding="utf-8")
    else:
        require(
            json.loads(record.read_text(encoding="utf-8")) == observed,
            "Artifact provenance mismatch",
        )
    print(json.dumps(observed, indent=2))


if __name__ == "__main__":
    main()
