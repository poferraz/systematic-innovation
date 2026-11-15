# Task 9 input-accounting verification

Baseline: `main` at `d64e5394d5c30a9128ee50c3a91181e8226b5b82`; local branch `codex/task9-input-preflight`. Scope: the owner's input-accounting/preflight request. **Zero actual provider requests and zero generation calls** were made. All HTTP replies in tests are synthetic, and Task 9 tests deny socket/DNS connections.

## Evidence and implementation

The provider's [counting guide](https://developers.openai.com/api/docs/guides/token-counting) documents a full-input count including roles/boundaries. Its [reference](https://developers.openai.com/api/reference/resources/responses/subresources/input_tokens/methods/count) defines the projection/result; its [Help Center](https://help.openai.com/en/articles/4936856-understanding-and-counting-tokens) identifies counting as free and separate from inference quota. These establish the accounting method, not actual account access or observations. Local tiktoken framing remains uncertified.

`counting.py` preserves exact input fields, rejects unknown/mutated settings, binds the complete generation request and count projection, and validates strict count-only replies. `HTTPCountTransport` fixes the route and enforces 10 seconds / 4 KiB with no retries. A generation transport passed by mistake is rejected before sending. Configured transport identities are immutable.

`Task9Guard.process_with_counter()` defers every counter until actual authorization, pause, source, scope, identity, pending-turn, budget and concurrency checks have passed. `count_ledger.py` fsyncs separate one-shot count claims/receipts, enforces at most 70 attempts, preserves failure/unknown outcomes and detects missing/corrupt evidence. Generation still has its existing independent 70-attempt / US$5 / no-retry limits. A completed generation is replayed without any counter call; authoritative counts must equal observed input usage.

Technical verification reconstructs every request, reconciles count and generation receipts, retains counts separately from inference/spend/output totals, and binds fresh-process resume to the first two count events and marker. Standard effect-bearing reports remain isolated and content-blind. The [launch packet](task9-launch-preflight.md) and [machine report](../evidence/study/task9-launch-preflight.json) explicitly deny launch and leave operator evidence unfilled.

## Test-first record

- Counter/transport RED cases covered absent implementation, mutable identity, generation-route misconfiguration and request mutation. Focused GREEN: **110 passed**, or **120** including the unchanged local tokenizer tests.
- Guard/ledger RED cases covered missing lazy processing, missing durable metadata, unretained evidence injection and a late count reaching generation. Focused GREEN: **97 passed** including existing guard regressions.
- Worker RED demonstrated an eager counter running before a refusing guard. GREEN moved it behind the guard; the worker suite passed **50** tests.
- Preflight RED demonstrated missing command/module and three scope mismatches accepted by the preflight but refused by execution. GREEN: **6** tests, including no traffic, unchanged pause files and nonzero blocked status.
- Verifier RED covered malformed/partial/mismatched count evidence, deadlines/order, live-without-counts and resume tampering. Two final regressions demonstrated a four-event prefix falsely claiming two events and a marker symlink opened before safe-path refusal. Focused GREEN: **23 new tests**; existing verifier behavior remains covered by the full suite.
- Review reproduced a full-wall omission: an initial count outside the generation-only timing span could falsely pass a combined 10,800/10,805-second run. Both regressions now refuse. The guard additionally reserves complete phase deadlines before claims; **8 focused wall tests passed** after RED reproduced fresh-count, cached-count and local-generation boundary breaches.

## Final verification

Run from the repository root:

```bash
python3 -m unittest discover tests -v
python3 tools/validate_skill.py skills/systematic-innovation
python3 -m tools.repository.authority
python3 -m tools.repository validate
python3 -m tools.repository acceptance --evidence evidence/architecture/acceptance.json --stage full
git diff --check
```

From `benchmark/`, with uv 0.12.8 and separate locked Python 3.11/3.13/3.14 environments:

```bash
uv lock --offline --check
uv run --offline --locked pytest -q
uv run --offline --locked ruff check .
uv run --offline --locked mypy src task9
uv run --offline --locked python -m task9 preflight
```

The preflight deliberately exits **1** with a blocked JSON packet; this is the expected result.

Final coordinated results on frozen source:

- Root: **181 passed**.
- Benchmark: **592 passed on each of Python 3.11, 3.13 and 3.14**, with no skips. Matrix runtimes were 360.08 / 352.95 / 369.94 seconds respectively.
- Ruff passed; Mypy passed **35 source files** on all three interpreters. Offline lock validation resolved the unchanged **36 packages**; no dependency was added or changed.
- Skill validation, authority/public-tree checks, whitespace checks and full **AR-01 through AR-12** acceptance passed, retaining implementation/protocol scope.
- The full counted integration passed the 70-count / 70-generation fixture schedule, zero-extra-request replay, fresh-process count-prefix resume, complete usage reconciliation and technical-only verification. These are synthetic callbacks, not API requests or model measurements.
- Independent review cleared all findings after scoped re-review. It separately exercised a synthetic future-live 70/70 path with valid temporary approvals and fresh-process resume; actual study flags stayed untouched and actual network requests remained zero.
- The saved preflight report was regenerated after final code fixes and checked against current source/profile digests. It reports launch blocked, zero provider requests and all operator requirements unfilled.

Final test commands explicitly removed `OPENAI_API_KEY` from the inherited environment. No merge or push was performed.

## Remaining launch boundary

No actual count/usage equality or endpoint/model access was measured; fixtures prove implementation behavior only. Account/project, provider policy, externally enforced spend/filesystem/egress controls, a clean reviewed immutable revision/config and separate owner approval remain required. The proposed additional 70 count requests are default-denied and have not been authorized or sent. Preregistration, stage/readiness authorization and the dry-run proposal remain unchanged; scientific gates remain pending.

Canonical skill SHA-256: `d5971f6e3e646916e2a287c5a8fde96a93b811ed071c362526c605ef222a890b`. The entire skill tree remains unchanged. This work includes no merge, push, private-pack access, human labeling or study advancement.
