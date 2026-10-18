# Bounded diagnostic amendment, before additional calls

The first revised candidate produced 590 and 630 words against 450. These are
retained failures in `after/skill_treatment.jsonl`, case `tight-budget`, reps 1–2.
The suspected cause is full prose plus field repetition overwhelming a budget
instruction without per-section allocations. Competing explanation: stochastic
instruction following. Change only the compact word allocation, retaining all
normal count targets and naming budget reductions honestly.

Allocate four of the eight unused initial-diagnostic call slots to two fresh
450-word retests and two exact-prompt final checks of an already-run public
development case. This is not an untouched holdout. The two reserved public
holdout cases still run once, after the final pack freeze. Total authorized
ceiling remains 111 calls. The finite-space reproducer consumes the last two
slots of the originally reserved 36 correction calls. No formal stage advances.

The allocation-only retest still failed (455 and 606 words). The next and final
two reserved calls test a narrower cause: the router said “deliver” the target
count, and the core did not explicitly require choosing a budget-feasible count
before drafting. Change “deliver” to “target” and make an explicit budget-limited
portfolio take precedence. Stop budget revisions after these two calls whether
they pass or fail; retain the regression if unresolved. This uses the four
amended slots in total, not an additional unbounded cycle.
