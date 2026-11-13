# GPU CI: rent only after the cheap checks

This CLI needs no GPU. This is a design for a separate CUDA workload, not a reason
to attach a GPU to the budget calculator. No GPU resources have been rented.

## Execution

Use one short-lived Runpod Community Cloud on-demand Pod with an L4 GPU, one GPU per
job. Require the chosen CUDA/runtime image by digest. Keep the tested wheel and
the workload image version with each result.

Release: after lint, source tests and artifact checks pass, run a deterministic
small correctness fixture, CPU/GPU result comparison with stated tolerance,
device allocation, one forward/backward pass and an explicit memory limit test.
Nightly: the same checks plus a larger fixture and a short throughput/memory
regression check against a stored baseline. Thresholds belong to the workload;
they are not invented for a CLI that does no tensor work.

Only trusted main commits and release tags may allocate. Never run fork PR code
on a persistent self-hosted runner. Use a fresh Pod and a single-use runner
registration, remove the runner afterward, and give the workload no provider key.
The trusted controller keeps that key, creates the Pod, and deletes it.
There is no provider/OIDC federation assumed here: the controller needs its own
scoped, rotated credential.

## Monthly planning numbers

Budget rate: **$0.44/GPU-hour**. Runpod's pricing page listed that Community Cloud
L4 rate when checked on 2026-11-13. It is a planning input, not a reserved quote.
Recheck current price, region, capacity and GPU availability before implementation.
Runpod advertises per-second billing; the calculator uses a conservative one-minute
quantum so this fixture can also expose per-allocation rounding errors. All default
durations are whole minutes, so that choice does not change the default total.

| Schedule | Runs | Test + startup | GPU hours | Compute USD |
| --- | ---: | ---: | ---: | ---: |
| Nightly | 30 | 12 + 3 min | 7.50 | 3.30 |
| Release | 4 | 30 + 3 min | 2.20 | 0.97 |
| Total | 34 | | 9.70 | **4.27** |

If every run consumes a second full attempt, the compute allowance is **$8.54**.
Use **$15/month** as a planning cap with room for storage and price variation;
this is a cap, not a forecast of the provider's invoice. Network, storage and tax
must be added for an actual deployment. No persistent network volume is required.

## Keep failures cheap

- Allocate only after CPU checks pass. Cancel superseded nightly work.
- Concurrency one; no automatic retry for test failures. Allow one retry for a
  classified infrastructure failure. Include startup in the allocation timeout.
- Hard allocation lifetimes: 20 min nightly, 40 min release. The controller
  stops/deletes a Pod on success, failure, timeout and cancellation.
- A separate five-minute reaper deletes expired Pods by owner/run/expiry labels.
  A workflow `finally`/`always()` alone is insufficient if the runner disappears.
- Reserve the worst-case job cost before allocation. Stop admission at the
  monthly cap. Provider alerts are a backup, not enforcement.
- Logs, GPU model/driver, billed lifetime and results go to CPU-hosted storage.
  Deleting the Pod also removes its ephemeral disk. Check retained volume costs.

Timeout ceilings make the “all jobs hang” compute envelope larger than the
normal-duration retry number: `(30 × 20 + 4 × 40) × 2 / 60 × 0.44 = $11.15`.
Cleanup lag and a higher on-demand price can increase it further.
The independent reaper and admission budget matter more than the nominal $4.27.

References: https://www.runpod.io/pricing and https://docs.runpod.io/pods/billing.
The pricing page was checked on 2026-11-13. Billing documentation access and storage
rates must be confirmed before deployment; neither a live Pod nor a bill was tested.

