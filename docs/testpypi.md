# One-time TestPyPI setup

Create an account at https://test.pypi.org and verify the email address.
Under https://test.pypi.org/manage/account/publishing/ add a pending publisher:

| Field | Value |
| --- | --- |
| PyPI project name | `soup-gpu-budget-kreichik` |
| GitHub owner | `Kreichik` |
| Repository name | `soup-devops` |
| Workflow filename | `release.yml` |
| Environment name | `testpypi` |

The first successful tagged release creates the project. No API token is needed.
The GitHub environment name must match. For this TestPyPI experiment there is no
required manual approval in the workflow; production should have an explicit
release policy and protected tags/main.

After setup, tag a tested commit on main with `v0.1.0` and push the tag. Do not
reuse a version after a successful upload. `skip-existing` is deliberately off:
unexpected pre-existing files should stop the release, not silently pass.

Use separate dependency and package downloads when verifying a published release.
Fetch our exact version with `--index-url https://test.pypi.org/simple/ --no-deps`,
then install its dependencies from PyPI. Do not combine TestPyPI and PyPI using
`--extra-index-url`; pip does not treat that as a trusted primary/fallback order.

