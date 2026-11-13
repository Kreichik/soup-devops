# GPU budget, bad releases

A GPU CI bill estimator with a release lab attached. It never provisions a machine.

The example budgets 30 nightly runs and four releases. Each allocation includes
startup time and rounds up to the billing interval. A second number shows the
ceiling if every job uses its retry allowance. Two six-second jobs on minute
billing cost two minutes, not one. That is the small detail this CLI exists to catch.

```console
python -m venv .venv
# Linux/macOS; on Windows use .venv\Scripts\activate
source .venv/bin/activate
python -m pip install .
gpu-budget
gpu-budget --plan "my plan.toml"
```

Copy [the example plan](src/gpu_budget/profiles/demo.toml) to change the numbers.
Default compute estimate: **$4.27/month**, or **$8.54** at the retry ceiling.
These are assumptions, not a provider quote. Storage, traffic and tax are extra.

## The release experiment

`Naive CI` tests the source on Linux/Python 3.12. `Release checks` builds a wheel
and sdist, then installs the same wheel on Linux, Windows and macOS with Python
3.10, 3.12 and 3.14. Installation runs outside the checkout in a fresh venv.
There is also a cold dependency resolution on 3.10, an sdist install, and an
offline Docker run with a read-only filesystem.

| Branch | User-visible failure | Why naive CI misses it |
| --- | --- | --- |
| `incident/python310` | `tomllib` is missing on Python 3.10 | Source tests run on 3.12 |
| `incident/windows` | Unix-only `pwd` import | Source tests run on Linux |
| `incident/package-data` | Bundled cost plan missing from wheel | File exists in the checkout |
| `incident/entrypoint` | Installed command points to a missing function | Tests call `main()` directly |

The broken branches are intentional. Do not use them for releases.
Run links and exact failure messages belong in [the evidence table](docs/evidence.md).

## Release path

`v0.1.0` must match both distribution versions. Publication requires all checks,
a commit already on `main`, and TestPyPI Trusted Publishing configured for
`Kreichik/soup-devops`, workflow `release.yml`, environment `testpypi`.
Only the publish job can request an OIDC token. Nothing publishes to real PyPI.
No `pull_request_target` workflow, credentials in checkout, or shared pip cache.

The build writes filenames, SHA-256 hashes, commit and ref to `release/record.json`.
Every consumer checks that record. Downloads use the artifact from the current
workflow run, not “the latest successful build.” The publish job checks again and
uploads those bytes without rebuilding. After publication it downloads the exact
version from TestPyPI, compares both file hashes and runs the downloaded wheel.

## Local checks

```console
python -m pip install --require-hashes -r requirements/ci.lock
ruff check .
ruff format --check .
PYTHONPATH=src python -m unittest discover -s tests -v
python -m build --no-isolation --outdir release/dist
python -m twine check --strict release/dist/*
python scripts/artifacts.py record
python scripts/smoke.py release/dist/*.whl
python scripts/smoke.py release/dist/*.tar.gz --cold
docker build -t gpu-budget-smoke .
docker run --rm --network none --read-only gpu-budget-smoke
```

`PYTHONPATH=src` above is for source unit tests only. Artifact tests remove it.
Shell wildcard examples use bash; on PowerShell pass the actual distribution path.
The build directory must be empty before a new build; CI gets a fresh checkout.

The CI lock targets the Linux/Python 3.12 build toolchain. The runtime lock is
used across the consumer matrix. To refresh hashes, use pip-tools 7.6.2:

```console
pip-compile --generate-hashes --allow-unsafe --no-emit-index-url --no-emit-trusted-host -o requirements/ci.lock requirements/ci.in
pip-compile --generate-hashes --no-emit-index-url --no-emit-trusted-host -o requirements/runtime.lock requirements/runtime.in
```

Review dependency changes before committing a new lock. A hash identifies the
chosen bytes; it does not tell you whether those bytes are safe.

## Notes

- [Submission note](docs/report.md)
- [GPU CI design and cost](docs/gpu-ci.md)
- [What AI did](docs/ai-use.md)
- [TestPyPI setup](docs/testpypi.md)

