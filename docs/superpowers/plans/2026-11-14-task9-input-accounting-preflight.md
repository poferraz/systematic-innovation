# Task 9 input accounting and launch preflight implementation plan

> **For agentic workers:** Use superpowers:subagent-driven-development or superpowers:executing-plans task by task. This implements the owner's request to resolve input accounting and prepare reviewable preflight evidence with zero generation calls.

**Goal:** Replace the unproven live framing estimate with guarded, request-bound provider counting and prepare an honest, blocked launch packet.

**Architecture:** The existing external worker obtains an authoritative count inside the same locked authorization boundary as generation. A separate durable ledger permits at most one count attempt per turn and 70 total; generation remains limited to 70 attempts / US$5 / no retries. Offline replay and local tokenization remain explicitly synthetic or uncertified.

**Tech stack:** Existing Python 3.11–3.14, standard-library TLS transport, Pydantic contracts and pytest; no new dependency.

**Spec:** Implements the full-input bound and launch requirements in [Task 9](2026-11-14-study-task9-six-case-feasibility.md), under the approved behavioral/repository specifications. It does not change skill behavior, scientific gates or execution authorization.

## Constraints and evidence

- Zero generation calls and zero actual provider requests during implementation; tests use synthetic replies and deny network connections.
- Preserve the entire canonical skill, draft preregistration, false stage/readiness live flags, and dry-run proposal.
- Provider documentation describes an exact count including roles/boundaries: [counting guide](https://developers.openai.com/api/docs/guides/token-counting). The [reference](https://developers.openai.com/api/reference/resources/responses/subresources/input_tokens/methods/count) defines the projection and response. The [Help Center](https://help.openai.com/en/articles/4936856-understanding-and-counting-tokens) says counting is free and separate from inference quota. These are documented guarantees, not an observed account-access test.
- The proposed future launch must explicitly authorize up to **70 count-only HTTP requests plus 70 generation requests**. Counting receives its own ceiling, 10-second deadline, 4 KiB response cap and no retries. The generation budget/caps remain unchanged. No count traffic is authorized by the current readiness record.
- The count projection preserves `model`, `instructions`, complete ordered `input`, `reasoning`, `text`, `tools`, `tool_choice`, `truncation`. Only the fixed generation-only `max_output_tokens`, `service_tier`, `store` fields are omitted. Unknown/mutated fields refuse rather than disappear.
- The provider count response has no model echo or generation response ID. Retain the requested model, both request digests, account/project, HTTP request ID, validated raw count response/hash, and timestamp; do not fabricate a provider attestation or zero-retention promise.

## Alternatives considered

1. Certify the local framing allowance: rejected because no reviewed model-specific framing proof supports it.
2. Authoritative provider counting: selected because the documented count includes request framing without inference. Approval and durability must precede this traffic.
3. Use generation probes or change the model/input/budget limits: excluded by the owner's zero-generation instruction and approved scope.

## Review focus

1. A networked counter must never run before approval, pause, scope, identity, pending-turn, budget and concurrency checks.
2. A completed generation replay must invoke neither counting nor generation; ambiguous count attempts must never retry.
3. Count evidence must bind every instruction, disclosure, prior assistant turn and fixed parameter to the exact generation request.
4. A count over 32,768 or malformed count must stop before generation; later provider usage must match an authoritative count.
5. Preflight must expose missing operator controls and remain blocked; neither a successful fixture nor a self-reported boolean grants launch permission.

## Task 1 — Guarded metadata boundary

Files: `benchmark/task9/contracts.py`, `guards.py`, new `count_ledger.py`; focused guard/count-ledger tests.

- [x] Add failing tests for the five review conditions, including expired/mismatched approval, false pause flags, concurrent lock, count deletion/tampering, 32,768/32,769, and crash/cache recovery.
- [x] Extend `InputBound` with optional strict `ProviderCountEvidence`. Add separate default-denied count authorization/70-request ceiling to `ExecutionApproval`.
- [x] Implement `Task9Guard.process_with_counter(job, payload, counter, send, *, transport_live)` with lazy counting under its existing lock. Keep `process(..., input_bound, ...)` for offline compatibility and reject uncertified/unretained live evidence.
- [x] Fsync a count claim and started receipt before calling the counter; retain completed evidence or a code-only failure. Cache only matching complete evidence. Count failures stop the run; metadata attempts never consume or enlarge generation limits.
- [x] Run focused tests, Ruff and Mypy; retain RED/GREEN results.

## Task 2 — Count-only provider adapter

Files: new `benchmark/task9/counting.py`; modify `transport.py`; focused counter/transport tests.

- [x] Write failing tests for exact projection, response strictness, unsafe/unknown fields, independent identity, malformed/duplicate/nonfinite/oversized data and count-only TLS routing.
- [x] Implement `counting_profile()`, `build_count_payload(payload)`, `ProviderInputCounter(transport).bound(payload)` and `HTTPCountTransport(account_id=..., project_id=...)`. The counter exposes `provider_counting=True`, transport mode/identity and its profile digest.
- [x] Reuse direct TLS/deadline/redaction mechanics with two fixed routes; expose no arbitrary endpoint or retries. Count transport enforces 10 seconds / 4,096 bytes.
- [x] Return `InputBound` with retained provider evidence; real endpoint evidence can certify framing, while offline evidence remains explicitly offline and local `tokens.py` stays uncertified.
- [x] Run focused tests, Ruff and Mypy; retain RED/GREEN results.

## Task 3 — Worker, verifier and review packet

Files: `worker.py`, `cli.py`, `verifier.py`, new `preflight.py`, tests and Task 9 documentation.

- [x] Route every worker counter lazily through the guard; live CLI selects provider counting while the existing early pause still refuses before credentials or provider traffic.
- [x] Add an offline 70-turn count-plus-generation fixture proving exact 70/70 cardinalities, pause/resume, no retries, redaction, cached replay, count/usage equality and technical-only reports. Existing local replay remains valid offline.
- [x] Extend technical verification to reconcile present count evidence without treating it as inference, output usage, spend or scientific evidence.
- [x] Implement a no-network preflight that reads actual code/config/source digests and reports the proposed count traffic, unchanged generation budget, accounting method, and unmet operator requirements. Its output always denies current launch authorization.
- [x] Retain a public proposed packet with account/project/control evidence unfilled, a technical accounting note and updated operations. Do not claim account access, OS isolation, budget enforcement or owner authorization from documentation alone.
- [x] Run root tests, all benchmark tests on 3.11/3.13/3.14, lock/lint/types/authority/isolation/full acceptance and fresh independent review. Keep changes reviewable locally; no merge/push or live execution is included in this request.
