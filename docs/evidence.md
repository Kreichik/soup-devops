# Run evidence

## Hosted results, 2026-11-17

All four defects pass the naive workflow and fail the release workflow. The fixed
version passes the full 3×3 OS/Python matrix, sdist installation and offline Docker.
These are completed Actions runs; the failed steps and error messages were checked.

| Branch | Naive CI | Release checks | Result |
| --- | --- | --- | --- |
| Fixed `main`, `70c8059` | [GREEN](https://github.com/Kreichik/soup-devops/actions/runs/43439361001/attempts/4) | [GREEN](https://github.com/Kreichik/soup-devops/actions/runs/43439361009/attempts/4) | All checks pass; publish skipped on a branch push |
| `incident/python310` | [GREEN](https://github.com/Kreichik/soup-devops/actions/runs/43438988323/attempts/2) | [RED](https://github.com/Kreichik/soup-devops/actions/runs/43438988218/attempts/2) | Python 3.10 cannot import `tomllib` |
| `incident/windows` | [GREEN](https://github.com/Kreichik/soup-devops/actions/runs/43438988317/attempts/2) | [RED](https://github.com/Kreichik/soup-devops/actions/runs/43438988333/attempts/2) | Windows cannot import `pwd`; minimal Linux container also lacks a passwd entry |
| `incident/package-data` | [GREEN](https://github.com/Kreichik/soup-devops/actions/runs/43438988018/attempts/2) | [RED](https://github.com/Kreichik/soup-devops/actions/runs/43438987928/attempts/2) | Bundled TOML missing after installation |
| `incident/entrypoint` | [GREEN](https://github.com/Kreichik/soup-devops/actions/runs/43438989887/attempts/2) | [RED](https://github.com/Kreichik/soup-devops/actions/runs/43438989691/attempts/2) | Installed command imports missing `run` function |

Selected failed jobs, with exact observed errors:

- [Python 3.10 wheel](https://github.com/Kreichik/soup-devops/actions/runs/43438988218/job/133878313655): `ModuleNotFoundError: No module named 'tomllib'`.
- [Windows wheel](https://github.com/Kreichik/soup-devops/actions/runs/43438988333/job/133878349293): `ModuleNotFoundError: No module named 'pwd'`.
- [Linux container](https://github.com/Kreichik/soup-devops/actions/runs/43438988333/job/133878349169): `KeyError: 'getpwuid(): uid not found: 65532'`.
- [Missing data](https://github.com/Kreichik/soup-devops/actions/runs/43438987928/job/133878317848): `Invalid plan: [Errno 2] No such file or directory: '.../gpu_budget/profiles/demo.toml'`.
- [Console entry point](https://github.com/Kreichik/soup-devops/actions/runs/43438989691/job/133878391141): `ImportError: cannot import name 'run' from 'gpu_budget.cli'`.

The Windows defect is a Unix-only owner lookup. Its extra Docker failure is real:
UID 65532 runs the process but has no entry in `/etc/passwd`. Removing the lookup
in the fixed version avoids both assumptions; the estimator needs no OS account data.

## Earlier infrastructure failures

On 2026-11-13 the first upload was blocked by missing app access. After access was
fixed, GitHub refused to allocate runners because the owner's account had a billing
lock. Earlier attempts remain linked from each run's attempt selector. For example,
[main attempt 1](https://github.com/Kreichik/soup-devops/actions/runs/43439361009/attempts/1)
contains the annotation `The job was not started because your account is locked
due to a billing issue.` Attempts 2 and 3 had the same problem. These are not
counted as defect detection. No failed run was deleted.

## Local experiment, 2026-11-13

| Case | Commit | Source tests, Linux/3.12 | Built wheel, Linux/3.12 | Other check |
| --- | --- | --- | --- | --- |
| Fixed base | `f77683d` | PASS | PASS | Linux/3.10 Docker PASS; sdist PASS; offline Docker PASS |
| `incident/python310` | `851ffcd` | PASS | PASS | Linux/3.10 Docker FAIL: `No module named 'tomllib'` |
| `incident/windows` | `6a7ca68` | PASS | PASS | Windows execution pending |
| `incident/package-data` | `6d66d48` | PASS | FAIL | Bundled `profiles/demo.toml` absent |
| `incident/entrypoint` | `6809af6` | PASS | FAIL | `cannot import name 'run' from 'gpu_budget.cli'` |

Every incident distribution built successfully. The two Linux/3.12 artifact
failures happen when invoking the installed console command, not in the build.
The Python 3.10 check installs the wheel and resolves its declared `tomli`
dependency before starting the command. The broken version still fails because
it unconditionally imports the newer standard-library module.

Commands used (run inside each worktree; shared tool venv uses locked build deps):

```console
PYTHONPATH=src /workspace/soup-devops/.venv/bin/python -m unittest discover -s tests -v
/workspace/soup-devops/.venv/bin/python -m build --no-isolation --outdir release/dist
/workspace/soup-devops/.venv/bin/python scripts/smoke.py release/dist/*.whl
```

Python 3.10 Docker image:
`python:3.10-slim@sha256:6ff506466f8b1e981719b468cc0023b8ef000b983cdec0eafe119d01f379e31d`.
The wheel directory and workspace CA bundle were mounted read-only; dependency
installation used the inherited proxy with TLS verification enabled.

Additional checks on the fixed version:

- Ruff lint and formatting: PASS.
- `twine check --strict` on wheel and sdist: PASS.
- Installed wheel and sdist outside the checkout: PASS.
- Docker image build, non-root run with no network/read-only filesystem: PASS.
- `scripts/probe_guards.py`: changed artifact bytes, stale commit and wrong tag
  all rejected with the expected error. The original build was unchanged.

## TestPyPI

**Published and verified on 2026-11-17.**

- Tag: [`v0.1.0`](https://github.com/Kreichik/soup-devops/tree/v0.1.0), commit `c9a1fcb`.
- [Complete green release run](https://github.com/Kreichik/soup-devops/actions/runs/44036315529).
- [Publish job and post-index checks](https://github.com/Kreichik/soup-devops/actions/runs/44036315529/job/133880593029).
- [TestPyPI release](https://test.pypi.org/project/soup-gpu-budget-kreichik/0.1.0/).

The tag run passed all nine OS/Python cells, sdist and Docker checks. OIDC upload
succeeded. The workflow fetched both distributions from TestPyPI, compared their
SHA-256 hashes against the tested build, and ran the downloaded wheel in another
clean environment. Default cost, retry ceiling, a plan path containing spaces and
invalid input handling all passed. No manual publish approval or API token was used.

The tagged commit also has independent green branch runs:
[release checks](https://github.com/Kreichik/soup-devops/actions/runs/44036315327)
and [naive CI](https://github.com/Kreichik/soup-devops/actions/runs/44036315341).

## Maintenance notes from the actual run

GitHub warned that several pinned actions target Node.js 20 and are being forced
onto Node.js 24. The runs passed, but updating and reviewing those pins is still
maintenance work. `*-latest` runner images and hosted capacity also change; a
green run is evidence for that environment and time, not a permanent guarantee.

