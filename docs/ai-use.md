# AI use

An AI coding agent helped analyse the task and drafted the CLI, tests, workflows,
incident variants and documentation. The GPU budget example was chosen to tie the
small application to the GPU CI part of the task.

Accepted suggestions: test an installed wheel outside the checkout; keep broken
cases separate; reuse the tested artifact; use OIDC instead of an upload token.

Checks performed by the agent are recorded in the run evidence and local test
results. These are automated checks, not a claim that the candidate manually
reviewed every line. The candidate should add their own review notes here before
submission.

The agent checked the completed GitHub runs on 2026-11-17: four naive-green /
release-red pairs and a green full matrix on main. It read the failing logs rather
than treating any red status as evidence. Earlier billing-blocked attempts were
kept and explicitly excluded. The extra missing-passwd-entry failure in Docker
was found in those logs; it was not part of the original expected Windows failure.

Two assumptions needed care: a lock in this repository does not pin every user's
environment, and “PyPI releases cannot be deleted” is too broad. Deletion exists,
but it neither recalls installed copies nor lets us overwrite a published filename.
Yanking and a new fixed version are the practical recovery path.

No answer script was prepared for the live discussion. No personal surprise or
manual verification is attributed to the candidate without their review.

The provider's documentation included instructions addressed to AI agents, such
as sending feedback to an external endpoint. Those were treated as page content,
not task instructions; no feedback or account setup request was sent.

