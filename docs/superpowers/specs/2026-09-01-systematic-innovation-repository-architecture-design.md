# Systematic Innovation Repository Architecture Design

**Date:** 2026-09-01
**Status:** Approved repository architecture; pending coordinated implementation plan
**Project:** `systematic-innovation`

## 1. Summary

This specification defines how the `systematic-innovation` repository should preserve one behavioral authority while adding the evidence, distribution, security, and maintenance practices required of a credible public Agent Skill project.

The approved direction is **Approach B: canonical core plus evidence shell**.

The public skill remains a directly usable, provider-neutral canonical directory. Repository tooling and documentation form an evidence shell around that core: they validate it, package it, exercise it across hosts, and support public claims. They do not become competing sources of behavior.

This specification adds repository architecture to the approved behavioral contract in `2026-08-31-systematic-innovation-design.md`. It does not change the skill's behavior, benchmark safeguards, or the three existing implementation plans.

## 2. Document Authority and Scope

The project uses the following document roles:

1. `CONTEXT.md` is the durable narrative and decision history.
2. `docs/superpowers/specs/2026-08-31-systematic-innovation-design.md` is the approved behavioral and evaluation contract.
3. This document is the repository-architecture contract once reviewed and approved.
4. The three files under `docs/superpowers/plans/` are the current execution design for the skill, benchmark runner, and benchmark study.
5. A future coordinated implementation plan may map approved specifications to executable work, but it must identify conflicts explicitly and must not silently rewrite earlier decisions.

Approved specifications govern behavior and architecture within their declared scopes. An explicit later owner decision recorded in `CONTEXT.md` may supersede an older provision, but when it affects a contract the affected specification must be revised and approved before implementation crosses that boundary.

Plans are subordinate execution documents. A plan may identify a conflict or propose a specification amendment, but language inside a plan cannot amend or supersede an approved specification. If authoritative documents conflict, implementation must pause at that boundary until the specification change is approved and the resolution is recorded in `CONTEXT.md`.

## 3. Goals

The repository architecture must:

1. Preserve one editable behavioral authority for the public skill.
2. Keep the skill provider-neutral and usable without repository tooling.
3. Make generated artifacts reproducible and detect drift from canonical sources.
4. Separate public skill content, public benchmark machinery, and restricted evaluation evidence according to their different trust requirements.
5. Help a fresh coding agent find the correct context without creating a parallel documentation system.
6. Support compatibility claims through independent evidence for format, installation, discovery, activation, and behavior.
7. Improve quality through specific, auditable gates rather than a gameable composite score.
8. Adopt GitHub controls in proportion to the project's current risks and maturity.
9. Preserve the scientific safeguards of the approved benchmark design.
10. Allow future host support without making any host the behavioral authority.

## 4. Non-goals

This architecture does not:

1. Create per-host copies of the skill merely to advertise compatibility.
2. Introduce a second project-management or handoff hierarchy beside `CONTEXT.md`, the specifications, and the plans.
3. Copy private Clief Notes Method text, naming, or templates into this public project.
4. Reproduce Prime Agent's language, runtime, workflow count, contribution model, or release machinery without a project-specific need.
5. Treat repository polish, badge count, test count, or a maturity score as evidence of skill effectiveness.
6. Expose restricted cases, sealed labels, embargoed rubrics, or sensitive evaluation outputs to the public skill or ordinary CI.
7. Rewrite the three approved implementation plans as part of adopting this architecture.
8. Require generated distributions to be committed to version control.

## 5. Architectural Invariants

The following rules are mandatory:

1. `skills/systematic-innovation/` is the only editable authority for public skill behavior.
2. A generated file is never an editable behavioral authority.
3. A host adapter may translate discovery or activation mechanics, but may not redefine the skill's method.
4. No host-specific instruction file may outrank or silently override the canonical skill.
5. The canonical skill must remain understandable and usable independently of build, benchmark, release, or GitHub tooling.
6. Restricted evaluation material must never be loaded into skill construction, public development evaluation, ordinary CI, or automatic agent context.
7. Public compatibility language must not exceed the retained evidence on any claimed compatibility dimension for that host and version.
8. Validation dimensions remain separate. Passing one gate must not compensate for failure in another.
9. Repository documentation must follow a one-fact-one-authoritative-location rule and link rather than restate detailed contracts.
10. Generated or released artifacts must be traceable to their canonical inputs and tool version.
11. An implementation plan may execute an approved contract but may not amend or supersede one.

## 6. Canonical Core

### 6.1 Skill authority

The canonical public artifact is `skills/systematic-innovation/`, with `SKILL.md` as its entry point and relative references or assets where the approved behavioral design requires them.

This directory must conform to the open Agent Skills format and must not depend on a particular provider's global instructions, tool names, subagent system, or proprietary lifecycle. A host that supports the common skill format should be able to install the canonical directory directly.

### 6.2 Progressive disclosure

The skill entry point should contain activation guidance, essential workflow, and navigation to supporting material. Detailed method references may live in relative files when this improves context efficiency, but moving material out of `SKILL.md` must not make activation ambiguous or require repository-level documents at runtime.

### 6.3 No shadow authorities

Root agent instructions, contributor documents, benchmark prompts, examples, generated archives, and host adapters may point to or test the canonical skill. They must not contain an independently maintained copy of its behavioral instructions.

## 7. Context and Documentation Routing

The repository should provide a thin, provider-neutral root orientation layer. Its purpose is to tell a fresh agent:

1. what the project is;
2. which documents are authoritative for the task at hand;
3. which areas contain restricted or generated material;
4. which validation commands apply after those commands exist; and
5. where agent-specific mechanics end and project behavior begins.

The routing layer should link to the existing context, specifications, and plans rather than introduce a duplicated `docs/clief/`-style operating system. Host-recognized instruction filenames may repeat the same short routing information only when discovery requires them; they must point back to the same project authorities.

Historical material belongs outside active instruction paths and must be clearly marked non-authoritative. An archive directory should be introduced only when there is real retired material to preserve.

## 8. Evidence Shell

The evidence shell contains repository-level mechanisms that evaluate or transport the canonical core without changing it.

### 8.1 Deterministic validation

Validation should independently cover, as applicable:

1. Agent Skills format and metadata;
2. internal links and required files;
3. provider-neutrality and prohibited host authority;
4. source-isolation and secret scanning;
5. generated-artifact drift;
6. installation and activation smoke tests;
7. benchmark-runner correctness; and
8. documentation claims that have machine-checkable evidence.

Each failure should identify the violated invariant and the authoritative source to fix. Validators must not repair canonical content implicitly.

### 8.2 Distribution

The canonical skill directory is the primary installable form. Release archives or catalogs may be generated from it for convenience.

Every generated release artifact must:

1. be built from a clean, declared input set;
2. exclude benchmark secrets, restricted evidence, repository-only instructions, and unrelated source material;
3. carry or accompany version and provenance information sufficient to identify the canonical revision and build definition;
4. have a cryptographic digest recorded in release evidence;
5. reproduce byte-for-byte under the declared build environment after archive ordering, timestamps, permissions, paths, and other byte-affecting metadata are normalized;
6. carry verifiable authenticity evidence binding its digest to the source repository, revision, and build definition; and
7. pass installation validation from the released artifact rather than only from the working tree.

Authenticity may use a platform attestation or a portable signed-manifest mechanism. GitHub-specific attestation is an acceptable public-repository implementation but is not the behavioral authority and must have a documented verification path. The verification policy must identify the trusted signer or workload identity and define key or identity rotation and revocation. A checksum without an authenticated source is integrity evidence only, not proof of origin.

A packaging format whose outer container contains unavoidable nondeterministic metadata must define and digest a normalized canonical payload, document the excluded container fields precisely, and prove that those fields cannot alter installed content. A general nondeterminism exception is not permitted.

Committed per-host distributions are not the default. If future delivery constraints require them, drift checks must make divergence a blocking failure.

### 8.3 Host adapters

A host adapter is justified only after evidence shows that the canonical skill cannot be installed, discovered, activated, or exercised correctly on that host without a translation layer.

Before an adapter is accepted, its evidence must identify:

1. the host and tested version;
2. the demonstrated incompatibility;
3. why documentation alone is insufficient;
4. the smallest required translation; and
5. a test proving that the adapter preserves canonical behavior.

Adapters live outside the canonical skill and should be generated where practical. They may change packaging, paths, metadata, or activation hints, but not the method's behavioral requirements.

## 9. Compatibility Evidence Model

Compatibility is a matrix of independent evidence dimensions, not a binary badge or an ordered ladder. A host may support explicit invocation and behavioral execution without supporting automatic discovery. Passing one dimension therefore does not imply that another dimension passed.

Every host record reports each dimension separately:

| Dimension | Question answered | Allowed result states |
| --- | --- | --- |
| Format conformance | Does the canonical directory satisfy the declared Agent Skills format version? | `passed`, `failed`, `not-assessed` |
| Installation | Can the declared artifact be placed or registered using documented host mechanics? | `passed`, `failed`, `not-supported`, `not-assessed` |
| Discovery | Does the installed skill appear in the host's available-skill mechanism when the host exposes one? | `passed`, `failed`, `not-supported`, `not-assessed` |
| Explicit activation | Does deliberate invocation or loading activate the intended workflow? | `passed`, `failed`, `not-supported`, `not-assessed` |
| Automatic activation | Does representative natural-language input activate the skill without naming it when the host claims automatic discovery? | `passed`, `failed`, `not-supported`, `not-claimed`, `not-assessed` |
| Behavioral conformance | Do retained runs satisfy the selected invariants of the approved behavioral contract through the tested invocation mode? | `passed`, `failed`, `not-assessed` |

Public claims must enumerate the supported dimensions and limitations rather than compress them into one level. A broad compatibility profile may require several dimensions to pass, but that conjunction is a release claim policy, not an assertion that the dimensions are intrinsically ordered.

Evidence records must include the skill revision, artifact digest, applicable format version, host and host version, installation procedure, invocation mode, test scenario, execution date, result by dimension, retained run identifiers where applicable, and limitations. They must also identify the claim profile that consumed the evidence.

Retesting is required when a material change affects a claimed dimension, including a relevant skill revision, artifact or adapter change, host discovery or invocation change, installation-procedure change, or host release known to affect skill handling. Evidence that has crossed its declared review interval or is affected by an unassessed material change becomes `stale`; stale or failed evidence must downgrade or qualify the public claim. A version-number change alone need not invalidate unrelated dimensions when documented evidence shows that the relevant behavior did not change.

## 10. Trust Zones and Security Boundaries

The architecture uses three trust zones.

### 10.1 Public skill zone

This zone contains the canonical skill and public supporting references. It must be safe to publish, install, and load into an agent. It contains no credentials, executable benchmark harness, restricted cases, sealed labels, or hidden evaluation guidance.

### 10.2 Public benchmark laboratory

This zone contains the provider-neutral runner, public development cases, fixtures, schemas, and reproducibility documentation. It may execute model or host subprocesses and therefore requires explicit command boundaries, redacted logs, constrained credentials, timeouts, and validation of external outputs.

Benchmark code must treat skill output, model output, cases, and host output as untrusted data. Public development results may guide improvement only within the safeguards of the approved behavioral and benchmark specifications.

### 10.3 Restricted evaluation pack

Restricted cases, sealed annotations, adjudication material, and embargoed outputs remain outside the public Git repository and outside automatic agent discovery. Public code may validate their structure through content-free schemas, fixture substitutes, and digests, but ordinary CI must not require or expose their contents.

Keeping material outside Git prevents accidental publication but does not by itself create a sufficient security boundary. Restricted cases, raw restricted responses, diagnostic annotations, adjudication records, and unredacted restricted logs remain in this trust zone throughout their lifecycle.

Before public repository code receives restricted-pack access, the operator must verify and record:

1. a frozen, reviewed runner revision and dependency-lock digest;
2. a clean runner worktree whose executable inputs match the reviewed revision;
3. the restricted-pack digest and authorized study stage;
4. the exact provider, model, account, adapter, and invocation configuration;
5. filesystem access limited to declared inputs and controlled result locations;
6. network egress limited to declared model or infrastructure endpoints needed for the run;
7. filtered process environments and credentials scoped only to the authorized run; and
8. the operator approval required by the benchmark-study protocol.

Provider use must be an explicit data-custody decision. The restricted execution record must state applicable retention, training, logging, and regional-processing settings or limitations. A provider whose handling cannot satisfy the declared study policy is not eligible for restricted execution.

Restricted storage must use explicit access control and appropriate protection at rest. Backups, synchronization, search indexing, temporary files, caches, logs, exports, and deletion must follow a declared retention policy. Public manifests contain only content-free identifiers, counts, digests, and approved aggregate results; detailed access and execution records remain restricted.

The restricted preflight fails closed if the runner revision, worktree, dependency lock, pack digest, execution controls, provider policy, or operator authorization does not match the frozen declaration. Leakage, premature access, or contamination is handled according to the approved benchmark-study retirement and replacement rules; repository convenience never overrides those safeguards.

## 11. Quality Ratchet and Evaluation Discipline

Quality improves through independent evidence gates and explicit regression decisions.

The repository must not collapse skill quality, code correctness, security, compatibility, documentation, and benchmark outcomes into one maturity score. Such a score would hide blocking failures and invite optimization for the metric rather than the project purpose.

Instead:

1. each gate has a named scope and pass condition;
2. exceptions are explicit, time-bounded where appropriate, and retain rationale;
3. regressions remain visible rather than being offset by unrelated improvements;
4. benchmark changes preserve versioned cases, rubrics, runner configuration, and provenance;
5. comparisons use clean contexts and fair with-skill/without-skill controls;
6. behavioral judgments retain observable assertions and human review where automation is insufficient; and
7. development, restricted-validation, and sealed-test evidence expose different feedback according to their scientific role.

Public development evidence may provide detailed diagnostics and may guide candidate revision. Restricted validation may return only the preregistered release-eligibility decision to the candidate-development role. Case-level outputs, strata, directionality, failure categories, examples, annotations, and hidden labels from restricted validation may not guide revision. A failed candidate may be rejected, but any later candidate change must be justified independently by public development evidence.

The sealed test is terminal for the frozen candidate within that study. Its result proceeds to reporting and stopping, not candidate revision. Restricted case content or diagnostic outcomes may become future development input only after the affected cases are formally retired, the study is closed, replacement evidence is established, and the transition is recorded in `CONTEXT.md` or the applicable study decision record.

Continuous improvement may otherwise use public development cases, documented user feedback, defects, and compatibility failures.

## 12. Stage-Matched GitHub Maturity

Repository maturity is the ability of a contributor or reviewer to understand changes, reproduce claims, and detect relevant risk. Controls should be introduced when their protected workflow exists.

### 12.1 Foundation stage

Before implementation work begins, the project needs an established Git lineage. The repository also needs clear authority routing, license and security boundaries, exact local validation entry points once they exist, and protection against committing restricted material. Before public executable tooling is accepted, security documentation must provide a private reporting channel or identify the repository's supported private vulnerability-reporting mechanism.

### 12.2 Active development stage

When executable code and dependencies exist, continuous integration should run the relevant deterministic checks with least-privilege permissions, bounded timeouts, concurrency cancellation, and pinned third-party actions. Dependency updates should be reviewable and exercised by the same gates as ordinary changes.

### 12.3 External contribution stage

Contribution policy, issue forms, pull-request templates, ownership rules, and changelog fragments should be introduced when external contribution or multi-maintainer coordination makes them useful. Empty governance ceremony is not a substitute for clear review criteria.

### 12.4 Release and sustained-operation stage

Release automation becomes appropriate once the project publishes versioned artifacts. It should build from canonical sources, verify reproducibility and digests, attach verifiable provenance, and test installation from the released artifact rather than only from the working tree. Scheduled tests are appropriate for risks that change without repository commits, such as host-version compatibility or provider behavior; schedules should not merely repeat stable unit tests.

## 13. Documentation Maintenance

Documentation has distinct jobs:

1. `README.md` explains public purpose, use, installation, evidence status, and limitations.
2. `CONTEXT.md` preserves durable intent, decision history, and current phase.
3. Specifications define approved contracts.
4. Plans define approved execution sequences.
5. Security documentation explains reporting and the trust-zone model.
6. Compatibility evidence records substantiate host-specific claims.
7. Generated release metadata records artifact provenance.
8. Restricted operating records define access, provider handling, retention, and execution custody without exposing protected content publicly.

A claim should be maintained at its authoritative location and linked elsewhere. Validation should detect broken links, contradictory compatibility declarations, and generated documentation drift when those checks can be made deterministic. Documentation review remains necessary for semantic accuracy and should be part of any change that alters behavior, security boundaries, installation, or public claims.

## 14. Relationship to the Existing Plans

The three plans dated 2026-08-31 remain the current execution design and are not amended by this specification.

After this specification is approved, a coordinated planning phase must compare its requirements against the existing plans. That phase should preserve compatible tasks, identify genuinely new repository-architecture work, and expose overlaps such as README ownership, security documentation, CI, release packaging, fixtures, and compatibility testing. It must not create four isolated plans that assign the same files or claims to different tasks.

The coordinated plan cannot resolve a contract conflict by choosing one document or declaring that a plan supersedes a specification. It must stop the affected planning thread, propose the smallest necessary specification amendment, and resume only after that amendment is approved and recorded.

No implementation begins merely because the architectural direction or this written specification is approved. The coordinated plan remains a separate approval gate.

## 15. Failure and Recovery Rules

1. If a distribution differs from its declared canonical inputs, packaging and release fail.
2. If a host cannot meet a claimed compatibility dimension, that dimension is downgraded, qualified, or removed; unrelated dimensions retain their own evidence and the canonical behavior is not weakened to preserve a badge.
3. If an adapter changes behavior, it is rejected or the behavioral change is proposed through the normal specification process.
4. If restricted evidence enters a public or development context, affected evaluation material is quarantined and handled under the benchmark-study contamination rules.
5. If documentation and executable evidence disagree, public claims follow the evidence while the discrepancy is resolved.
6. If repository history cannot be recovered, the owner must explicitly approve a new lineage and record what provenance could not be preserved before implementation proceeds.
7. If a future repository control adds maintenance cost without protecting an active risk, it may be deferred with recorded rationale rather than satisfied cosmetically.
8. If restricted preflight cannot verify the frozen runner, clean worktree, dependency lock, pack digest, custody controls, provider policy, or operator authorization, the restricted run does not start.
9. If release authenticity or normalized reproducibility cannot be verified, the artifact is not published as an official release.
10. If a plan conflicts with an approved specification, work at that boundary stops until the specification is amended and approved.

## 16. Acceptance Evidence for This Architecture

Architecture acceptance is based on explicit evidence rather than subjective completion language.

| ID | Criterion | Required evidence | Pass condition | Authoritative record or gate |
| --- | --- | --- | --- | --- |
| AR-01 | One canonical public skill source | Source inventory and authority validation | Exactly one editable behavioral source resolves to `skills/systematic-innovation/`; generated artifacts and adapters point to it without independently maintained behavior | Repository validation evidence |
| AR-02 | Root orientation works from a clean context | Scripted fresh-agent walk using only repository-root discovery and no conversation memory | The agent identifies `CONTEXT.md`, both approved specifications, the applicable plan, generated areas, and restricted boundaries without loading unrelated documents as authority | Fresh-agent orientation evidence |
| AR-03 | Skill format, installation, and discovery claims remain separate | Declared-format validator result plus compatibility matrix records | Format passes the declared Agent Skills version; every installation and discovery claim has its own host-specific procedure and result | Format validation and compatibility evidence |
| AR-04 | Generated artifacts are isolated, reproducible, and authentic | Two clean builds, source-isolation scan, digest comparison, provenance verification, and install-from-release smoke test | Canonical payloads match byte-for-byte, prohibited content is absent, provenance verifies, and the released artifact installs successfully | Release gate and provenance record |
| AR-05 | Host adapters are evidence-gated | Demonstrated host delta, decision record, minimal adapter diff, and canonical-behavior preservation test | Each adapter addresses a recorded host limitation and passes the preservation test without introducing independent behavior | Adapter acceptance record |
| AR-06 | Compatibility claims match retained evidence | Compatibility matrix, claim-profile evaluation, and staleness review | Every public claim is supported on every claimed dimension; failed, unsupported, not-claimed, not-assessed, and stale dimensions remain visible | Compatibility release gate |
| AR-07 | Public CI is independent of restricted evidence | CI inventory, synthetic restricted fixtures, and negative secret/content scan | Public CI passes without a restricted pack and no workflow, artifact, cache, or log contains protected material | Public CI gate |
| AR-08 | Restricted execution fails closed | Restricted preflight record using synthetic fixtures plus controlled rehearsal of the custody protocol | Unapproved revision, dirty worktree, digest mismatch, undeclared provider, excessive access, or missing authorization prevents execution without exposing fixture content | Restricted execution authorization gate |
| AR-09 | Benchmark safeguards remain aligned | Cross-document traceability review and protocol tests | Splits, feedback boundaries, stage order, contamination response, human authorization, and stopping rules agree across approved specifications and study contracts | Benchmark study gate |
| AR-10 | Quality dimensions cannot offset one another | Gate inventory and representative failing fixtures | A failure in any blocking dimension remains blocking and visible; no composite score converts it into a pass | Merge and release gate definitions |
| AR-11 | GitHub controls are stage-matched | Current-stage risk-to-control record | Every enabled control names the active risk it mitigates; deferred controls record their trigger and rationale | Repository governance review |
| AR-12 | Document authority is unambiguous | Authority and conflict scan across context, specifications, and plans | No plan claims contractual supremacy; unresolved conflicts are recorded and block affected work | Specification approval and coordinated-planning preflight |

## 17. Deferred Decisions

The following decisions remain deliberately deferred until coordinated planning or empirical evidence makes them necessary:

1. the implementation language and exact commands for packaging and repository validators;
2. whether any host requires an adapter and, if so, which host is first;
3. the concrete filesystem layout for compatibility evidence and generated release metadata;
4. the release channel and versioning cadence;
5. the platform-specific attestation or portable signature implementation used to satisfy release authenticity;
6. the storage technology and provider allowlist used to satisfy restricted-data custody requirements;
7. the exact GitHub rulesets and features available to the eventual public repository;
8. when external-contributor governance becomes warranted; and
9. whether generated archives remain release-only or later need a committed catalog.

These choices may refine mechanics but must preserve the invariants in this specification.

## 18. Rationale

This architecture transfers the strongest structural lessons from the references without importing their project-specific machinery.

From the Clief Notes Method repository, it adopts a single editable authority, deterministic derivation, source isolation, explicit installation evidence, fixtures, and separation of active and retired material. It does not copy private content, create a parallel project-state hierarchy, or assume that every host needs a generated distribution.

From Prime Agent and current GitHub guidance, it adopts precise contributor instructions, risk-specific automation, least-privilege CI, reproducible and authenticated releases, dependency discipline, and evidence-backed public claims. It does not copy a mature runtime project's workflow volume before this repository has the corresponding code, contributors, or operational risks.

The canonical-core/evidence-shell boundary is the simplest design that keeps the skill portable while allowing the surrounding repository to become rigorous. Independent compatibility dimensions prevent convenient but false hierarchy claims. Trusted restricted execution protects scientific evidence when public code must process it. Verifiable release provenance allows consumers to authenticate what they install. Together these rules avoid both extremes: an under-specified Markdown artifact with unverifiable claims, and a distribution platform whose adapters and generated copies become the real product.
