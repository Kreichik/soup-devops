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

Two assumptions needed care: a lock in this repository does not pin every user's
environment, and “PyPI releases cannot be deleted” is too broad. Deletion exists,
but it neither recalls installed copies nor lets us overwrite a published filename.
Yanking and a new fixed version are the practical recovery path.

No answer script was prepared for the live discussion. No personal surprise or
manual verification is attributed to the candidate without their review.

