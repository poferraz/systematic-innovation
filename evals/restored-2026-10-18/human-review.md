# Human evaluation packet instructions

This public development packet is prepared, not completed calibration. No human
ratings or semantic quality scores have been supplied. Read `human-answers.json`
without opening `assignment-key.json` or source result files. Answer wording can
still reveal a method; this limits blinding even after assignment labels vanish.

Two trained reviewers independently read each complete user-disclosure script and
assistant conversation. First extract all actual proposals from the final answer,
recording source spans and parser misses/false positives. Separate provisional
seeds, components, examples, constraints, rejected/infeasible proposals, refusals,
and implementation steps. A self-check does not establish compliance.

Normalize each proposed mechanism into intervention, actor, changed flow, causal
operation, intended effect and principal constraint. Label equivalent mechanisms
by operation rather than shared vocabulary. Preserve disagreements and abstain
when domain expertise is needed. Check every earlier user constraint against the
actual causal chain, including hidden labour, authority and physical resources.

Use the anchored ratings in `evals/pilot/rubric.md`, supplemented by these
candidate-level anchors: relevance 0 unrelated / 1 tangential / 2 directly useful
to the stated goal / 3 specifically addresses the diagnosed tension; constraint
alignment 0 violates / 1 materially unresolved / 2 respects stated boundaries with
labelled uncertainty / 3 explains how each binds; causal clarity 0 slogan / 1
missing causal link / 2 intelligible intervention-to-effect chain / 3 precise
operation and dependencies; plausibility 0 impossible / 1 possible but materially
uncertain / 2 credible given resources / 3 well supported. Mark critical safety
or rights violations independently, with an evidence span for every rating.

Apply all five approved gates conjunctively, then deduplicate qualifying
candidates. Record raw candidates, raw semantic families, qualified candidates,
qualified distinct families, each rejection category, discovery burden,
preservation and scope failures. Efficiency uses all conversation output tokens,
including earlier questions; a missing denominator remains unknown.

For comparison, present paired answers from the same case in seeded random
order and in the reverse order, without condition/model/revision identities or
efficiency values. Record preference, reason, tie/abstention and order
inconsistency. Lock independent labels before adjudication. Keep expertise
requirements and unresolved causal identity visible.

This packet cannot pass the formal twelve-case rehearsal: that requires the
approved exact cases, five conditions, repetitions, at least 40 stratified
double-coded pairs, separate identity/gate agreement, pairwise agreement >=0.75
and Krippendorff alpha >=0.67. No automated headline claim is permitted without
those gates (or the approved human-primary fallback). Do not resample individual
answers as independent cases.
