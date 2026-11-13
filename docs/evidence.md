# Run evidence

## GitHub status

**Blocked before upload.** Both `git push` and the connected GitHub contents API
returned HTTP 403 (`Resource not accessible by integration`). The repository is
public and readable, but the connected installation currently lists only
`BAITC-Hacks`, not the personal account `Kreichik`.

There are no Actions run links yet. The owner needs to grant the GitHub app access
to `Kreichik/soup-devops`. No Windows/macOS run or OIDC publication is claimed.

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

## Still required

Push main and the four incident branches. Capture naive-green and hardened-red
Actions runs for each defect, plus a green run on main. Verify the actual failed
steps, not just workflow conclusions. Then publish a matching tag through TestPyPI
OIDC and check the fetched files against the tested hashes. Add those links here
without deleting or rewriting any failed runs.

