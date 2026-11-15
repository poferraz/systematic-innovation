# Restricted execution custody and authorization

Restricted validation and sealed evidence remain outside every public Git worktree,
public CI, release archive, automatic agent context, and ordinary development run.
This includes prompts, scoring labels, annotations, raw outputs, calibration material,
unredacted logs, temporary files, and case-level diagnostics. Public records contain
only approved logical identifiers, counts, digests, decisions, and permitted aggregate
results. A synthetic fixture is the only restricted-pack substitute used in public CI.

## Operator procedure

1. Freeze and independently review the runner revision, candidate skill, dependency
   lock, adapter and invocation. Use a clean dedicated worktree and `uv sync --locked`.
   Record full Git revision and SHA-256 digests. Do not modify the canonical skill as
   part of an execution run. Never grant an adapter access to an unreviewed checkout.
   Invoke the preflight module from that same reviewed checkout: its actual
   `__file__` must be the tracked `benchmark/src/systematic_innovation_bench/restricted_preflight.py`
   under the declared runner root, and its bytes must match that revision's Git blob.
   A checker imported from a different checkout cannot authorize the declaration.
   The checker is self-contained and imports only standard-library code and the
   Pydantic/PyYAML dependencies provisioned from the verified lock; it does not load
   another benchmark module to make the authorization decision.
2. Place the pack and results in separate controlled external locations. Apply explicit
   filesystem access control and encryption at rest. Results directories must exist
   with no group or other permission bits (for example mode `0700`). Exclude pack,
   results, caches, logs and exports from backups, synchronization and search indexing.
   Record custody review evidence and its digest; a boolean in YAML is not proof that
   encryption, provider policy, or operating-system isolation has been configured.
   The pack must be outside every Git worktree, including unrelated repositories and
   ignored directories. A `.git` directory or linked-worktree `.git` file anywhere
   above the pack makes both structural validation and preflight refuse access.
3. Declare the exact provider, model, account label, adapter and argument array. Verify
   retention, training, logging and regional-processing settings against study policy.
   An unknown or inadequate handling policy makes the provider ineligible. Record
   limitations in controlled custody evidence. Use scoped credentials for this run only;
   keep credential values out of declarations, command arguments, prompts and logs.
4. Configure actual process controls: read-only declared inputs, one controlled output
   location, endpoint-limited egress, an environment constructed only from approved
   keys, short-lived credentials, and a constrained adapter. Clear inherited proxies and
   loader hooks. The preflight rejects proxy and process-loader environment keys. Use
   the deployment platform's sandbox/firewall to enforce access; the Python preflight
   checks the frozen declaration and observed local state and does not install a sandbox.
5. Complete a declaration conforming to
   [`restricted-preflight.schema.json`](../../benchmark/schemas/restricted-preflight.schema.json).
   Start with the deliberately unauthorized
   [example declaration](../../benchmark/configs/restricted-preflight.example.yaml).
   Requested input/output access and egress/environment keys must remain within the
   approved allowlists. Do not authorize an ancestor of the pack or runner as an input
   root. Output must not overlap either input trust zone. Paths must be absolute,
   existing and free of symlinks. Keep the detailed declaration outside public Git.
6. An authorized operator records approval with approver label, timezone-aware timestamp,
   exact study stage, candidate SHA-256 and declaration SHA-256. `declaration_digest`
   computes SHA-256 over UTF-8 JSON with sorted keys, compact separators, no ASCII
   escaping, and only the `approval` field excluded. The approval binds every other
   declaration field. Approval is an operator attestation under controlled storage and
   access control; the file format does not authenticate a person's identity. Validate
   the approval's provenance through the organization's operator process.
7. Run `sib restricted-preflight --declaration DECLARATION --output AUTHORIZATION`.
   `--dry-run` performs checks without writing a record. The command does not invoke
   an adapter or execute a study. It verifies the actual Git HEAD and clean tracked
   and untracked worktree state, its executing source location and reviewed bytes,
   lock and candidate membership in the reviewed tree,
   exact digests, external pack boundary, controls, policies and operator approval.
   Approval and access controls pass before any pack bytes are hashed. Failures emit
   structural rule codes only. No authorization record is written on failure.
8. Immediately before separately authorized restricted execution, repeat preflight in
   the same controlled environment. Treat authorization as an observation of current
   state, not a reusable access token. Keep a run-specific authorization record and
   enforce the same digests and controls at the adapter boundary. Stop if any input,
   endpoint, policy, environment or storage control changes. Never let a development
   inbox or public result directory receive restricted responses.

## Digests and evidence

A regular file uses plain streaming SHA-256. A directory digest iterates regular files
in sorted POSIX relative-path order and hashes the UTF-8 filename, a NUL byte,
eight-byte big-endian file size, and streaming file bytes for each entry.
Symlinks and non-regular files are refused. Empty packs are refused.
Directory names and filesystem metadata are not included; relative filenames are.
The dependency lock is the reviewed runner's tracked `benchmark/uv.lock`.
The restricted-pack validator uses this same framing for exactly `scoring.yaml`,
`test.yaml`, and `validation.yaml`. Undeclared extra files or directories are refused,
so its summary `digest` is the same value as `digest_path(pack)` and the declaration's
`pack_sha256`. Per-file digests remain available separately.

Successful authorization exposes run and pack logical identifiers, stage, runner
revision, candidate/lock/pack/declaration/execution/custody-evidence digests, timestamp,
and check decisions. Detailed filesystem paths, provider account details, command
arguments, restricted records and credentials are absent from the returned record.
The public synthetic custody rehearsal and its refusal cases are in
[`test_restricted_preflight.py`](../../benchmark/tests/test_restricted_preflight.py).
They do not establish live provider eligibility or authorization for real packs.

## Lifecycle, feedback and incident response

Define retention and verified deletion before access. Keep temporary files in the
controlled encrypted location; disable unrelated caches and redact necessary logs
before append-only persistence. Apply the same exclusions and retention to exports,
backups, replicas and crash artifacts. Record deletion verification and revoke scoped
credentials at closure. A protected storage export requires an explicit operator
custody decision; never publish detailed declarations or case-level restricted data.

Validation returns only the preregistered release-eligibility decision to the candidate-development role. Do not expose case-level outputs, strata, effect direction, failure
categories, examples, annotations or hidden labels as candidate revision input.
Reject a failed candidate; justify any new revision independently with public
development evidence. The sealed test runs once on the unchanged frozen candidate
and proceeds to reporting and stop, without revision from its result.

On leakage, premature access or contamination, stop execution and preserve controlled
incident evidence. Revoke exposed credentials and access, contain copies and logs,
notify the operator, and document the incident without publishing protected content.
Retire any affected case before its content or diagnostic outcome can become future
development input. Close the study, establish replacement evidence, and record the
transition in `CONTEXT.md` or the applicable study decision record. A convenience
exception cannot authorize reusing contaminated held-out evidence.
