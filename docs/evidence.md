# Run evidence

## GitHub status

Main and all four incident branches are uploaded. The initial HTTP 403 was fixed
by installing the GitHub app for the personal account, not just the organization.

**Hosted execution is blocked by account billing.** Each initial run failed before
executing a step. GitHub's annotation reads:

> The job was not started because your account is locked due to a billing issue.

These are infrastructure failures, not evidence that a package defect was caught.
No green hosted run, Windows/macOS execution or OIDC publication is claimed.
The failed runs remain visible:

| Branch | Naive CI | Release checks | Actual outcome |
| --- | --- | --- | --- |
| `main` | [run](https://github.com/Kreichik/soup-devops/actions/runs/43438961713) | [run](https://github.com/Kreichik/soup-devops/actions/runs/43438961538) | Billing block |
| `incident/python310` | [run](https://github.com/Kreichik/soup-devops/actions/runs/43438988323) | [run](https://github.com/Kreichik/soup-devops/actions/runs/43438988218) | Billing block |
| `incident/windows` | [run](https://github.com/Kreichik/soup-devops/actions/runs/43438988317) | [run](https://github.com/Kreichik/soup-devops/actions/runs/43438988333) | Billing block |
| `incident/package-data` | [run](https://github.com/Kreichik/soup-devops/actions/runs/43438988018) | [run](https://github.com/Kreichik/soup-devops/actions/runs/43438987928) | Billing block |
| `incident/entrypoint` | [run](https://github.com/Kreichik/soup-devops/actions/runs/43438989887) | [run](https://github.com/Kreichik/soup-devops/actions/runs/43438989691) | Billing block |

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

After the owner resolves the GitHub billing block, rerun the workflows. Capture
naive-green and hardened-red runs for each defect, plus a green run on main. Verify the actual failed
steps, not just workflow conclusions. Then publish a matching tag through TestPyPI
OIDC and check the fetched files against the tested hashes. Add those links here
without deleting or rewriting any failed runs.

