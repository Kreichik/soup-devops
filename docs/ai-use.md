# AI use

## My role

I (Yan) supervised the work and configured GitHub access and the TestPyPI
Trusted Publisher. Codex drafted changes and executed the technical checks under
my direction. I agree with keeping manual approval for production PyPI until
main and release tags are protected and a release owner is assigned. The command
execution and log inspection described below were performed by Codex.

An AI coding agent helped analyse the task and drafted the CLI, tests, workflows,
incident variants and documentation. The GPU budget example was chosen to tie the
small application to the GPU CI part of the task.

Accepted suggestions: test an installed wheel outside the checkout; keep broken
cases separate; reuse the tested artifact; use OIDC instead of an upload token.

Checks performed by the agent are recorded in the run evidence and local test
results. These are automated checks, not a claim that the candidate manually
reviewed every line.

The agent checked the completed GitHub runs on 2026-11-17: four naive-green /
release-red pairs and a green full matrix on main. It read the failing logs rather
than treating any red status as evidence. Earlier billing-blocked attempts were
kept and explicitly excluded. The extra missing-passwd-entry failure in Docker
was found in those logs; it was not part of the original expected Windows failure.

The owner configured TestPyPI Trusted Publishing. The agent pushed `v0.1.0` and
verified the successful publish job, hash comparisons and post-index smoke test.
The email draft is provided for the owner to review and send.

Two assumptions needed care: a lock in this repository does not pin every user's
environment, and “PyPI releases cannot be deleted” is too broad. Deletion exists,
but it neither recalls installed copies nor lets us overwrite a published filename.
Yanking and a new fixed version are the practical recovery path.

No answer script was prepared for the live discussion. No personal surprise or
manual verification is attributed to the candidate without their review.

The provider's documentation included instructions addressed to AI agents, such
as sending feedback to an external endpoint. Those were treated as page content,
not task instructions; no feedback or account setup request was sent.

## Follow-up checks run by Codex under my direction

- Read `naive.yml` and `release.yml`. Traced the wheel and sdist from a single
  build through the install matrix, sdist and Docker checks to the tag-only
  TestPyPI job, which uploads the same files and checks the published copies.
- Opened the [green Naive CI run](https://github.com/Kreichik/soup-devops/actions/runs/43438988018/attempts/2)
  and the [red installed-wheel job](https://github.com/Kreichik/soup-devops/actions/runs/43438987928/job/133878317848)
  for `incident/package-data`. GitHub showed exit code 1 on the installed-wheel
  step and required access for the full log. In a local copy with the incident's
  packaging settings, all four source tests passed on Windows with Python
  3.14. The wheel built, but it lacked `profiles/demo.toml`. The installed
  `gpu-budget` exited with code 2 because that file was missing.
- Downloaded version 0.1.0 from TestPyPI, matched the wheel's SHA-256 against
  `docs/evidence.md`, and installed it in a fresh Windows Python 3.14 venv.
  From outside the checkout, `gpu-budget --version` returned 0.1.0 and
  `gpu-budget` reported $4.27/month and an $8.54 retry ceiling.
