# A green job is not an installed package

The application estimates a GPU CI bill. It includes startup, per-allocation
billing rounding and a retry ceiling. The default is $4.27/month of compute;
GPU execution itself is a design exercise, not a paid resource in this repository.

## Reproduce, then catch

Four incident branches each contain one real defect: unconditional `tomllib`
import on Python 3.10, Unix-only `pwd` import on Windows, missing bundled TOML,
and a broken console entry point. The naive workflow tests source on Linux/3.12,
so all four pass the equivalent local source checks. The release workflow tests
the installed distribution.
Actual run links and outcomes are recorded separately in `docs/evidence.md`.
The first hosted runs were blocked before any step by GitHub account billing;
they do not count as successful defect detection. Windows execution is pending.

The build produces a wheel and sdist once. A 3×3 OS/Python matrix installs the
wheel in empty venvs outside the checkout, invokes the installed command and
checks its output. Python 3.10 also resolves from wheel metadata with no cache.
A source-distribution install and offline Docker run cover two other paths.
The matrix samples 3.10, 3.12 and 3.14; it does not prove every interpreter works.

## Three quiet failures addressed

**Stale or replaced artifacts.** Each run uploads a uniquely named artifact.
Consumers download from that run and verify its hashes, commit and ref.
Publication reuses those bytes. It never rebuilds or selects the “latest” run.
This catches accidental substitution, not an attacker who controls the builder.

**Tag/version mismatch.** The tag must equal both wheel and sdist metadata
versions. A publish-time ancestry check requires the tagged commit to be on main.
Repository settings must still protect main and restrict who can create tags.

**PR credentials.** PR checks get read-only permissions and checkout does not
persist credentials. The OIDC job runs only on tag pushes in this repository,
after all checks. There is no `pull_request_target` or privileged PR execution.
TestPyPI trusts the exact repository/workflow/environment; no upload token exists.

Actions are pinned by commit. Build and smoke dependencies have hash locks.
Fresh installs and a cold resolver path reduce cache-induced false confidence.
A lock is not a malware check, and it does not freeze consumer dependency choices.

## GPU cost and control

Use ephemeral Runpod GPU Pods for a separate CUDA workload: small correctness
tests per release, a larger fixture and regression sample nightly. At an assumed
$0.44/hour, 30 × 15 minutes plus 4 × 33 minutes is 9.7 hours, or $4.27.
Full-duration second attempts cost up to $8.54. A 20 GB ephemeral disk adds about
$0.03 at the normal duration; Runpod lists no transfer fees. With timeout-length
attempts the compute envelope is $11.15, before cleanup lag, disk and tax. Budget $15 and
recheck the live price before deploying. Detailed assumptions are in `gpu-ci.md`.

Run CPU checks first; cap concurrency, time and retries. A trusted controller
holds the provider credential. A separate expiry reaper handles orphaned Pods;
cleanup inside the workflow alone cannot survive loss of that runner.

## Verdict

I would let this pipeline publish this demo to TestPyPI without a manual gate.
I would not yet give it unattended real-PyPI publication. First protect the main
branch and release tags, confirm the post-index check on a real publication, and
assign an owner for release incidents. Then decide whether this package's blast radius
justifies removing approval. The choice is a policy, not a consequence of green CI.

Remaining gaps include compromised maintainers/actions/build tools, untested
Python versions and architectures, future dependency changes, index propagation,
and application behavior beyond the smoke fixture. OIDC authenticates a workflow;
it does not certify the code it uploads. PyPI supports deletion and yanking,
but neither recalls installed copies or permits overwriting published filenames.
Recovery is normally a yank plus a new fixed version.

## Observation and concern

The source tests can execute the CLI function successfully while the installed
command is unusable. The boundary between the checkout and the wheel was the
useful part of this experiment. My remaining concern is how easily “same commit”
gets mistaken for “same artifact”: rebuilding in the publish job would undo much
of the evidence gathered earlier.

AI assisted with code and text; its scope and review limitations are recorded in
`ai-use.md`. The evidence table distinguishes completed checks from pending work.
