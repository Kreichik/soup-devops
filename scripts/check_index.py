"""Fetch the exact TestPyPI release and compare it with the tested build."""

import hashlib
import json
import time
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import urlparse
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]


def main():
    record = json.loads((ROOT / "release/record.json").read_text(encoding="utf-8"))
    endpoint = f"https://test.pypi.org/pypi/soup-gpu-budget-kreichik/{record['version']}/json"
    for attempt in range(12):
        try:
            with urlopen(endpoint, timeout=20) as response:
                release = json.load(response)
            break
        except HTTPError as exc:
            if exc.code != 404 or attempt == 11:
                raise
            print("Index not visible yet; retry in five seconds", flush=True)
            time.sleep(5)
    files = {item["filename"]: item for item in release["urls"]}
    if set(files) != set(record["sha256"]):
        raise RuntimeError("Index filenames differ from the tested build")
    destination = ROOT / "release/published"
    destination.mkdir(exist_ok=True)
    for name, expected in record["sha256"].items():
        item = files[name]
        url = urlparse(item["url"])
        if url.scheme != "https" or url.hostname != "test-files.pythonhosted.org":
            raise RuntimeError(f"Unexpected TestPyPI file host: {url.hostname}")
        with urlopen(item["url"], timeout=30) as response:
            content = response.read(10 * 1024 * 1024 + 1)
        digest = hashlib.sha256(content).hexdigest()
        if digest != expected or item["digests"]["sha256"] != expected:
            raise RuntimeError(f"Published bytes differ: {name}")
        (destination / name).write_bytes(content)
        print(f"Verified TestPyPI bytes: {name} sha256:{digest}")


if __name__ == "__main__":
    main()
