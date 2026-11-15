# Task 9 launch preflight — proposed, blocked

Prepared under the owner's instruction to resolve input accounting and prepare a reviewable launch packet with **zero generation calls**. This work makes **zero actual provider requests**. Live studies stay paused and the canonical skill stays frozen. The machine-readable companion is [launch-preflight.json](../evidence/study/task9-launch-preflight.json); regenerate it after source/config changes.

## Accounting resolution

The local tiktoken profile remains uncertified. Live input accounting instead uses the documented `POST /v1/responses/input_tokens` contract: the provider includes request framing in its count. Each prepared transcript is counted separately, after authorization and before generation. See the [counting guide](https://developers.openai.com/api/docs/guides/token-counting) and [reference](https://developers.openai.com/api/reference/resources/responses/subresources/input_tokens/methods/count).

The count projection preserves the selected model, instructions, every ordered user/assistant message, reasoning/text settings, tools, tool choice and disabled truncation. It omits only the fixed generation-only storage, tier and output-limit fields. Both the original generation request and the count projection are hashed. The retained count reply contains the numeric count and its documented object type; a local receipt also records HTTP request ID, requested snapshot, account/project and timestamp. The endpoint does not return a model echo or generated response ID, so the receipt does not invent either.

The controller holds one lock through validation, counting and generation. It checks actual approval, scope, source, identity, pending turn, pause and budget before counting. A durable claim precedes each count request. Any error, timeout, ambiguous completion, invalid evidence or count above **32,768** stops before generation. Count and generation requests have no retries. A completed generation is returned from cache without another count; retained count evidence supports interrupted preparation without duplicate traffic. Observed generation input usage must equal the authoritative count. Offline fixtures remain synthetic and cannot authorize a launch.

## Traffic and budget proposed for later approval

| Control | Proposed launch limit |
| --- | --- |
| Generation requests | 70 maximum, exactly the existing 30 jobs / 70 required turns |
| Count-only requests | **70 maximum, separately authorized**, at most one per turn |
| Total HTTP requests | At most 140; no probes, warm-ups, retries or judges |
| Count billing | Provider currently documents counts as free and outside normal inference quota; [billing explanation](https://help.openai.com/en/articles/4936856-understanding-and-counting-tokens) |
| Generation usage cap / stop | US$5 / US$4.50 including uncertainty; US$0.05 reservation per attempt |
| Token limits | 32,768 full input / 4,096 total output per generation |
| Time / response limits | Count: 10 seconds / 4 KiB; generation: 120 seconds / 1 MiB |
| Concurrency / wall window | One combined operation at a time / three hours |

The timeout envelope is `70 × (10 + 120) = 9,100 seconds`, leaving 1,700 seconds for local overhead and deliberate resume within the three-hour window. A timeout stops the run; this is scheduling headroom, not permission to continue after a failed attempt.

The guard reserves the full remaining deadlines: a fresh count requires more than 130 seconds left, and generation after a fresh or cached count requires more than 120 seconds. It measures from the earliest retained count/generation event and refuses before the next phase claim. Final verification independently rejects a completed combined span reaching three hours. Completed generation replay consumes no new deadline or request allowance.

The existing owner decision approved 70 generations / US$5 / zero retries and offline readiness work. It did **not** approve these additional count requests or live generation. `ExecutionApproval` now defaults count permission to false/zero; a later reviewed launch must explicitly set count permission/limit and update the actual owner decision. Generation caps are unchanged.

## Operator evidence still required

| Requirement | Current status |
| --- | --- |
| Exact account/project and scoped credential custody | Unfilled; no credential was requested or accessed |
| Actual snapshot and count-endpoint access | Unverified; public documentation is not an account-access test |
| Current price, tier and data-policy review | Public model/rates checked; actual account policy pending |
| Enforcing dedicated-account/project or external spend control | Operator evidence pending; code does not establish account isolation |
| Filesystem and egress controls | External enforcement evidence pending |
| Clean reviewed revision, executable config and source/lock/corpus/skill digests | Must be frozen after review; current packet reports actual revision/dirty state |
| Explicit count-traffic approval and Task 9 live execution authorization | Not issued |

The verification controller needs read-only public source, corpus, skill and run evidence to perform its checks. The transport receives only the opaque request projection. An operator must specify an enforceable process/container policy consistent with those reads; an outbox-only filesystem rule for the entire controller would prevent verification. The only proposed network destinations are direct TLS requests to the two fixed API paths. Redirects, proxy routing and arbitrary endpoints are refused by the transport.

Counting lacks a `store` parameter. Neither count receipts nor `store: false` on generation establish zero provider retention. Review the actual account's [data controls](https://developers.openai.com/api/docs/guides/your-data). Only public development material is in scope.

## Review and launch sequence

1. Review implementation, offline evidence and the proposed extra metadata traffic. Run `uv run --offline --locked python -m task9 preflight` from `benchmark/`. Its current blocked packet exits **1**, makes no provider request and grants no permission.
2. Supply the missing operator evidence outside public Git. Freeze a clean reviewed revision and regenerate all approval bindings, including the counting profile and lock.
3. Issue a separate owner decision for Task 9 only, explicitly covering account/project, count and generation ceilings, custody controls, technical-only review and unchanged skill. Bind it to the exact run/config/source identities.
4. Only after that authorization, prepare a fresh executable config/run. Preserve this dry-run proposal and keep every later scientific stage pending.

The six-case technical study itself has not run. No account access, observed provider counts, empirical performance, operating-system enforcement or launch authorization is claimed by this packet.
