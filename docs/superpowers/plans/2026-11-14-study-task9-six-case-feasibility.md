# Study Task 9 — six-case technical feasibility proposal

**Status:** Owner approved the plan/budget and readiness implementation on 2026-11-14; live execution remains unauthorized.

**Prepared:** 2026-11-14, America/Vancouver.

**Baseline:** `main` at `afe1a36507f0fe6be3f9db1c3a763eaface19d25`; GitHub CI passed.

**Proposed API usage authorization:** **US$5 maximum**, 70 generation requests, zero automatic retries, one request at a time.

**Deliverables:** this plan, [`feasibility-six.proposed.yaml`](../../../benchmark/configs/feasibility-six.proposed.yaml), the external [worker/guards/verifier](../../../benchmark/task9/README.md), and [offline verification evidence](../../../benchmark/task9-verification.md). No live generation is authorized.

This plan executes the approved [behavioral specification](../specs/2026-08-31-systematic-innovation-design.md) §§18–26, [repository specification](../specs/2026-09-01-systematic-innovation-repository-architecture-design.md) §10, and [Study Task 9](2026-08-31-systematic-innovation-benchmark-study.md). It does not amend them. The current [stage contract](../../../benchmark/study/stage-gates.yaml) remains unauthorized/pending and [preregistration](../../../benchmark/study/preregistration.yaml) remains draft. The skill pack stays frozen; its `SKILL.md` SHA-256 is `d5971f6e3e646916e2a287c5a8fde96a93b811ed071c362526c605ef222a890b`.

## 1. Decision proposed for review

Use one dated model snapshot, **`gpt-5.4-mini-2026-03-17`**, through the runner's existing **inbox/outbox protocol** and a separately reviewed OpenAI Responses API worker. This is a technical plumbing check, not a test of which condition wins. One model and host keep execution faults easy to attribute; this provides no cross-model or host-generalization evidence.

At plan approval, the worker did **not exist as a reviewed live adapter in this repository**. The generic subprocess adapter and offline fake are not an OpenAI API integration. Worker implementation, offline verification, its immutable revision, the account/project selection, and exact budget authorization are prerequisites to a later live launch. The subsequent owner instruction authorizes implementing and offline-testing the worker, guards and verifier; it authorizes none of those live operations.

| Approach | Tradeoff | Proposed disposition |
| --- | --- | --- |
| Dated GPT-5.4 mini snapshot + metered API worker | Exact model version, observed usage, explicit price envelope; requires a reviewed worker | Recommended |
| Existing Codex CLI / subscription | Familiar installed host, but still needs a turn-protocol bridge; subscription use does not establish a measured API dollar price or a hard per-run cost ceiling | Defer |
| GPT-5.6 Luna API | Lower listed token price; its current model page exposes the undated `gpt-5.6-luna` identifier rather than a dated snapshot | Available alternative for a separately revised proposal; no silent fallback |

OpenAI lists the selected dated snapshot and standard rates of **$0.75 per million input tokens and $4.50 per million output tokens**. Sources checked on 2026-11-14: [model/snapshot](https://developers.openai.com/api/docs/models/gpt-5.4-mini), [pricing](https://developers.openai.com/api/docs/pricing). These rates are assumptions to refresh before authorization, not evidence that a particular account has access.

## 2. Exact scope and request count

All cases are public development cases. Use all five main conditions: `vanilla`, `generic-brainstorm`, `format-matched`, `established-method`, `full-skill`; one model, one inbox host, one replicate, no ablations.

| Case ID | Interaction | Assistant requests per condition | Requests across five conditions |
| --- | --- | ---: | ---: |
| `syn-dev-001` | Deep: initial prompt plus two fixed disclosures | 3 | 15 |
| `red-dev-001` | Deep | 3 | 15 |
| `sys-dev-001` | Deep | 3 | 15 |
| `pre-dev-001` | Quick | 1 | 5 |
| `tri-dev-001` | Quick | 1 | 5 |
| `adv-dev-001` | Deep | 3 | 15 |
| **Total** | **Four Deep, two Quick** | **14 across the six cases** | **70** |

`6 cases × 5 conditions × 1 replicate = 30 parent jobs`. These are **70 assistant generation requests**, not 30 requests. Each condition receives byte-identical case prompts and ordered user disclosures; only the declared condition instructions vary. The runner's stable order is sorted by case ID, so the first case is `adv-dev-001`, not the order of the comma-separated selection.

**Budget reconciliation required:** the draft preregistration currently says `max_calls: 50` and `retry_limit: 1`; 50 does not cover even this no-retry run. The proposal is a **stage-specific 70-call, zero-retry override**, requiring an approved decision record and reconciliation of the draft budget before launch. Passing current schema validation does not approve this override. Do not change the draft or stage status merely to make a command run.

## 3. Proposed model and adapter contract

| Setting | Proposed value |
| --- | --- |
| Provider / endpoint | OpenAI direct API; `POST https://api.openai.com/v1/responses` |
| Model allowlist | Exactly `gpt-5.4-mini-2026-03-17`; refuse unavailable or substituted models |
| Account / project | Operator-selected, dedicated metered project, logical identity and remaining budget recorded before launch; not selected or accessed now |
| Reasoning / text | `reasoning.effort: none`, `text.verbosity: medium`, identical for all arms |
| Serving tier | `service_tier: default`; no Fast/Priority, Batch, regional-endpoint switch, tool or search charges |
| Output / input | At most 4,096 provider output tokens; at most 32,768 full request input tokens, including instructions, prior assistant output, disclosures and protocol overhead |
| Context | Stateless reconstruction from the supplied transcript; no `previous_response_id`, server conversation, automatic compaction, hidden memory or prior-condition output; `truncation: disabled` |
| Tools | `tools: []`, `tool_choice: none`; no browsing, filesystem tools, MCP, external retrieval or autonomous subagents |
| Sampling | Omit temperature, top-p and seed; use supported provider defaults uniformly. Do not claim deterministic outputs. Preserve the exact request parameters |
| Persistence | `store: false`; full redacted provider response/usage retained locally under controlled runtime storage |
| Transport | Non-streaming, 120-second total request deadline, 1 MiB response cap, one outstanding request, no hidden SDK/client retries |
| Authentication | Scoped project credential supplied only through `OPENAI_API_KEY`; environment name only in config, no values in prompts, manifests, argv, diagnostics or public Git |
| Paths / egress | Worker can read only its approved opaque outbox and write its response/ledger paths; canonical evidence writes belong to `sib ingest`. Independently enforce endpoint allowlisting and filesystem scope |

These settings configure the **measurement harness**, never the skill. Full treatment loads the entire canonical pack through `planner.load_skill_pack`; the worker must not discover extra repository instructions or add different system prompts by condition. Supply each `TurnJob.system_instructions` as the one designated instruction block and replay every transcript message verbatim in role/index order. Provide no treatment labels, source mappings, scoring rubric, gold information or other condition's answer to the generator.

For each opaque `turn_id`, the worker accepts exactly one provider attempt and writes one correlated `TurnResponse` with its exact `job_id`, requested assistant `turn_index`, `attempt: 0`, final assistant text/refusal, integer `usage.input_tokens`, integer `usage.output_tokens`, cost provenance, latency and completion status. Extract all applicable assistant text/refusal content rather than assuming the first provider output item is the answer. Retain the redacted complete response, request ID, returned model/tier, usage breakdown and finish reason. Missing/corrupt usage is a stop condition, never a tokenizer estimate presented as observed metadata.

Use the provider's total `output_tokens`, including non-visible output, consistently across all arms. The cap includes those tokens; do not add `reasoning_tokens` a second time or substitute visible-text length. Preserve any reported breakdown separately. See [token-accounting documentation](https://developers.openai.com/api/docs/guides/token-counting). A cap-related incomplete response is a failure to review, not a reason to increase limits or regenerate that condition.

`cost` is a **conservative token-rate calculation**, not an invoice field: `(reported_input_tokens × 0.75 + reported_output_tokens × 4.50) / 1,000,000`. Charge all input at the uncached rate for the ceiling, retaining cache details separately; do not assume credits or cache discounts. Label technical cost totals as calculated upper bounds, and reconcile account usage separately. No per-dollar usefulness claim is authorized.

`store: false` is not a zero-retention promise. Provider abuse-monitoring retention and account policy still apply; only public development material is eligible here. Review the actual account policy before approval. [OpenAI data controls](https://developers.openai.com/api/docs/guides/your-data) describes the default training exclusion and retention limitations. No restricted-pack access or restricted preflight is needed for this public-only stage.

## 4. Budget and resource envelope

USD API usage, excluding tax/foreign-exchange fees and labor. No credits, caching discounts, tool fees or subscription valuation are assumed. This is a ceiling calculation, not a prediction that outputs will hit their caps.

| Item | No-retry proposal |
| --- | ---: |
| Maximum billable generation attempts | 70 |
| Maximum full input tokens | `70 × 32,768 = 2,293,760` |
| Maximum all-assistant output tokens | `70 × 4,096 = 286,720` |
| Input charge bound | $1.72032 |
| Output charge bound | $1.29024 |
| **Token-price bound** | **$3.01056** (round outward: **$3.02**) |
| Per-request runtime reservation | **$0.05**, above calculated maximum `$0.043008` |
| **Runner reserved envelope** | **70 × $0.05 = $3.50** |
| **Requested usage cap** | **$5.00** |
| **90% operational stop threshold** | **$4.50**, including outstanding reservations |
| Paid judge / embedding / human-calibration API calls | **0** |
| Paid model-access probes / warm-up / automatic recovery calls | **0** beyond the 70; perform readiness checks without generation |

If a different endpoint, rate, model, output/input cap, tool, retry or extra probe is needed, stop and revise the proposal; do not spend the buffer implicitly. One retry for every planned turn would mean **140 calls**, 4,587,520 input tokens, 573,440 output tokens, a **$6.02112** price bound, **$7.00** reserved envelope, and a separate suggested **$10.00** cap. That alternative is **not included** in the recommended $5 proposal.

Engineering/operator planning allowances, not measured estimates: allow **4–8 hours** to implement and independently review a new API worker/guards if none can be reused; **up to 2 hours active operator time** for readiness and technical verification; reserve a **3-hour wall-clock execution window**. At 120 seconds per request, the 70-request timeout envelope is 140 minutes before local overhead and the deliberate resume pause. A timeout stops the run, so this is scheduling headroom, not permission to keep retrying. No hourly labor rate was supplied; these hours are not included in the $5 API cap. The subsequent owner instruction authorizes readiness implementation and offline tests. It does not authorize live execution or paid operator engagement.

## 5. What is enforced today, and what must be ready first

| Control | Current `benchmark/` core | Required before later authorization |
| --- | --- | --- |
| Model allowlist, 70 dispatch ceiling, known $0.05 per-turn reservation, $5 total | Enforced during planning/reservation; cost ledger uses the greater of reservation and reported cost | Verify the external worker makes no generation request outside a matching reserved opaque turn |
| One outstanding inbox request | `export` enforces `max_concurrency: 1` | Worker must enforce the same limit, including on restart |
| No retries / failure stop | `retry_limit: 0`; `failure_threshold: 0.0` stops after any returned `failed` response | Disable automatic retries at every SDK/HTTP layer; reconcile an ambiguous in-flight request before any new dispatch |
| 4,096 output cap | Forwarded in parameters | Worker must send the cap, validate returned usage and finish reason, and refuse mismatches |
| 32,768 input cap | **Not a RunConfig field or core guard** | Reviewed worker must prove a conservative full-input bound before transmission, including protocol overhead. Prefer exact local tokenization for the pinned model with validated message overhead; reject uncertainty. No silent truncation. No unbudgeted provider token-count requests |
| $4.50 stop at 90% | Declared in study rules; **not implemented by core** | Durable external guard checks `max(calculated_usage, reserved_cost)` plus outstanding requests before each send; an account alert is not a substitute for a hard guard |
| Timeout / 1 MiB cap / scoped environment | Subprocess adapter has controls; **inbox worker does not inherit them** | Worker/network platform must enforce them explicitly |
| Execution pause | Draft flags and `dry_run: true` preserve this proposal; **stage authorization is not read by CLI** | Separate explicit owner approval and a launcher that refuses absent/mismatched approval; never give an unattended worker an executable config while paused |
| Frozen source / skill | Source digest guards mutations; skill is read from canonical path | Freeze and record reviewed worker/runner commits, lock and corpus hashes, full skill-tree digest and expected `SKILL.md` hash before launch |
| Technical-only reporting | Current `sib report` includes effect/count/stratum fields | Reviewed isolated verifier produces only a whitelisted technical summary; keep full report/score artifacts unopened by the study operator for Task 9 |

The required worker/launcher/verifier are **readiness work**, now authorized for implementation and offline tests; they were not tested capabilities at plan approval. Their implementation plan must use RED → GREEN tests for wrong model/tier, token/cost cap breaches, unknown usage, over-size/timeout, ambiguous completion, duplicated/replayed turns, leaked credentials, absent approval and the 90% stop. An actual full-input upper bound is necessary to make the dollar ceiling credible. Do not infer safety from the schema-valid dry run below.

## 6. Sequence for a later, separately authorized execution

### A. Safe preparation now — no run artifacts or model calls

From `benchmark/`:

```bash
uv run --locked sib validate --config configs/feasibility-six.proposed.yaml
uv run --locked sib plan --config configs/feasibility-six.proposed.yaml --cases cases/development --case-ids syn-dev-001,red-dev-001,sys-dev-001,pre-dev-001,tri-dev-001,adv-dev-001 --preregistration study/preregistration.yaml --run-dir runs/study9-feasibility6-proposal-20261114 --dry-run
```

Expected: `dry_run: true`, `parent_jobs: 30`, `maximum_calls: 70`, `maximum_cost: 3.5`, `maximum_output_tokens: 286720`. No run directory, exported packet, network generation request or stage change. Current price-dependent assumptions are not validated by these commands.

### B. Readiness and approval — still no live generation

1. Complete the separate worker/guard/verifier implementation and synthetic offline tests; review the code and pin its revision. Preserve provider SDK dependencies outside the core, with their own exact lock if needed.
2. Verify snapshot access for the selected account without a generation probe, endpoint/tier/data policy, scoped credential handling, and an enforcing project/external spend guard. No credential values enter the approval packet.
3. Rerun the root and benchmark checks from `AGENTS.md`, verify a clean reviewed checkout and whole skill-tree identity, and freeze the six-case corpus/scripts, runner source, lock, adapter, parameter and plan digests. No user-facing state is frozen merely by writing this draft.
4. Obtain an explicit decision for **Study Task 9 only**, listing account/project logical ID, selected model/adapter, 70 calls, $5 cap, $4.50 stop, one-at-a-time operation, zero retries, input/output/time limits, technical-only review and no skill edits. Reconcile the draft 50-call budget through that reviewed stage decision. Approval of this plan alone is not execution authorization unless the owner explicitly says so.
5. After that separate authorization, make a new immutable executable config/run ID from this proposal (`dry_run: false` only in the approved copy). Record the exact approval/config digests and study stage. Keep the reviewed proposal unchanged. Do not authorize Task 10 or private studies.

### C. Execute via inbox — do not perform these steps now

Use existing `sib plan`, `export`, `ingest`, `resume`, `score`, `report`, and `verify-run` interfaces described in `benchmark/HANDOFF.md`, together with the separately approved worker/verifier. Do not substitute `sib run` with the fake adapter or pass a Codex CLI directly as if it already spoke the turn protocol.

- Export one new opaque pending turn to a fresh run-local outbox; check approval, source, input and spending guards; send at most one provider request; persist the redacted response and durable external request ledger; ingest exactly the matching response. Never resend an already processed opaque turn ID.
- After the first Deep assistant turn has been **ingested and durably checkpointed**, deliberately stop the worker before exporting its next turn. The first sorted case is `adv-dev-001`; expected next assistant index is **4**, following the next fixed user disclosure. Record accepted-turn bytes/digest and dispatch count.
- Resume from a fresh process, verify prior evidence unchanged, then export the next deterministic disclosure. This pause should add **zero generation calls**; do not interrupt an in-flight request to manufacture a retry test.
- Continue the fixed schedule across all arms. A justified refusal is a preserved observation; do not bypass it or shorten Deep schedules selectively. A refusal that prevents required protocol coverage leaves the technical gate incomplete.
- Unknown completion after timeout is ambiguous spending: stop/quarantine, recover existing evidence or reconcile with provider/request IDs. Do not automatically resend. If there is no recoverable response, retain missingness and an incomplete decision.
- Stop generation after all 30 jobs terminate. No extra examples, reruns, alternate models, extractions by model, judges or later-stage cases may be requested from the remaining budget.

## 7. Technical verification, judging scope and decision

Required gate: **zero protocol/integrity failures**. `verify-run` proves artifact integrity, not scientific or technical feasibility by itself.

| Check | Required evidence / pass condition |
| --- | --- |
| Coverage and correlation | Exactly the six IDs/five conditions/one replicate; 30 distinct terminal parent records, at most 70 unique provider attempts, exact opaque IDs/indices/attempts; every required turn covered |
| Disclosures | Four Deep cases use exactly three assistant turns each per condition; both scripted user disclosures are byte-identical across all five arms, regardless of questions; Quick cases have one assistant turn |
| Resume | Recorded checkpoint after first Deep acceptance; same accepted bytes/digest after fresh-process resume; no extra attempt, regenerated success or duplicate dispatch |
| Append-only evidence | Requests/responses, failures/refusals, reservations and transitions preserved; valid durable tails recover; no overwritten raw records; digests verify |
| Usage and ceilings | 100% provider input/output-token metadata for every actual attempt; all-turn totals reconcile; returned model/tier/finish reason recorded; observed usage/cost bounds and limits pass |
| Redaction and execution limits | Synthetic offline sentinel tests for worker/runner canonical files, errors and reports; no real key inserted into a prompt; offline negative budget/concurrency/input/output/approval tests pass |
| Judge construction | Build **12** blinded order-swapped pairwise packets: six cases × full-skill vs format-matched × two orders, one declared protocol-check family, one criterion (`constraint_alignment`). Preserve complete user transcripts; hide identities, token/cost formula and source mappings. No judgment requests are sent. Exercise five-criterion packet construction with synthetic extracted candidates offline; never fabricate ratings for real output |
| Reports | Generate and hash standard Markdown/JSON outputs through a role-separated process; verify their integrity without opening effect-bearing content. Produce a whitelisted technical Markdown/JSON decision record containing only stage IDs, revision/digest evidence, coverage/status counts, parity/resume checks, metadata completeness, calculated resource totals, limit checks, exclusions/deviations and gate decision |

**Zero paid judge calls and zero human-calibration labeling are budgeted.** Reliability, judge acceptance, actual preference judgments and at least 40 double-coded blinded calibration pairs belong to Task 10. Packet generation checks interface plumbing only. Keep private assignment keys and any future blinding seed outside rater-accessible Git (F-31).

`score` must not invent quality; missing/unrated quality remains missing. The current standard reports expose primary effects, win/tie/loss, mechanisms, condition/stratum summaries and sensitivity contrasts. Their generation is permitted only inside the technical verifier boundary for this stage; do not print/open/inspect rankings or condition effects, or present a provisional zero as useful performance. An unavailable quality endpoint is expected here. The whitelisted technical verifier is a prerequisite, not a claim about an existing `--technical-only` CLI option.

Allowed terminal statuses are `succeeded`, `failed`, `refused`, `budget-stopped`. Lawful refusal with complete required technical coverage can be a valid outcome. `failed`, a budget stop, missing coverage, unresolved spending or absent usage must be retained but yield **stopped/incomplete**, not an automatic pass. After an operator-reviewed pass, record only the technical decision and run digest as the Task 9 gate evidence. Keep Task 10 and every later stage pending; no automatic advancement and no skill revision from this run.

## 8. Stop conditions

Stop before the next send, preserve evidence, and leave the gate incomplete if any condition below applies:

- No matching execution approval, unreconciled 50/70-call draft budget, unreviewed worker/verifier, dirty or changed runner/adapter/skill/corpus/config, or missing account/model access.
- More than 70 generation attempts would be required, any retry is proposed, more than one request is outstanding, wall-clock execution reaches three hours, or a transport deadline expires. No hidden preflight generation or SDK retries.
- Conservative calculated spend or reservations including unresolved requests reach **$4.50**; a next request could breach the **$5** cap or its **$0.05** ceiling; pricing/tier/endpoint changes; or provider usage cannot be reconciled.
- Full input exceeds 32,768 tokens or its bound is unknown; output exceeds 4,096, ends incomplete/cap-truncated, is empty without a valid recorded refusal, has missing/malformed token metadata, or returns an unexpected model/tier/tool call.
- Any failed provider attempt (`failure_threshold: 0.0`), unknown completion, correlation/order/parity mismatch, duplicate success, changed prior record, integrity failure, unredacted credential, unexpected filesystem/egress access or non-public material.
- Completion of the authorized 30 jobs. This is the normal stop; make only the technical gate decision afterward.

Do not raise caps, add models/conditions, silently restart under another ID, tune the skill, or spend the unused balance on debugging calls. Any later corrected run needs a new reviewed run/version and explicit decision; do not use sealed-study restart rules as authorization for Task 9 retries. Safety incidents stop/quarantine immediately. Preserve negative outcomes and report the technical reason without leaking credentials or interpreting condition effects.

## 9. Review checklist and preparation evidence

- [x] Owner accepts the model/snapshot, direct API route and technical-only construct.
- [x] Owner approves the stage-specific **70 calls / $5 / no retries / concurrency 1** decision; the scoped readiness record reconciles the budget while preregistration stays draft.
- [x] External worker, approval/spend guards, durable ambiguity handling and technical verifier are implemented, offline-tested and independently reviewed; final command evidence is retained separately.
- [ ] Provider-framing evidence certifies the complete live input bound. The implemented local tokenizer profile remains uncertified and blocks live dispatch.
- [ ] Exact account/project, provider policy, model access, enforcing budget control, revisions/digests and a clean checkout are recorded.
- [ ] A separate explicit live execution authorization is issued. **Not issued now.**

Preparation evidence (2026-11-14):

- `sib validate` accepted the proposed config and reported `dry_run: true`.
- The exact `sib plan ... --dry-run` command above produced 30 parent jobs, 70 maximum calls, 286,720 maximum output tokens and a $3.50 reserved maximum. Its JSON floating-point value was `3.4999999999999982`; the budget arithmetic uses decimal $3.50.
- Independent decimal recomputation confirmed 2,293,760 input tokens and a $3.01056 token-price bound. No generation, judge or provider-access probe was made.
- The proposal run directory does not exist. Preregistration is still `draft`, `execution_authorized` is still false, Task 9 is still pending, and the frozen skill hash matches. No existing study/skill files were edited.
- A separate read-only reviewer checked the protocol, arithmetic, actual runner controls, source documentation and launch blockers, and found no material contradictions. This is a review of the proposal, not study approval.
- Repository authority/isolation validation and whitespace checks are run against the prepared artifacts before handoff.

The owner subsequently approved the 70-call/$5/no-retry plan and readiness implementation with offline tests. See `benchmark/study/task9-readiness-approval.yaml`. Synthetic offline exports are permitted for tests; live generation, scientific stage advancement, private-pack access, merge and push remain unauthorized.
