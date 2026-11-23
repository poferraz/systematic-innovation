# Reproducible Release, Attestation, and Verification Guide

This document defines the build, verification, origin-attestation, identity-rotation, and revocation procedures for official `systematic-innovation` releases under [`docs/specifications/repository.md`](specifications/repository.md) (§8.2) and [`release/policy.json`](../release/policy.json).

---

## 1. Canonical Input & Normalization Contract

- **Canonical behavioral source:** [`skills/systematic-innovation/`](../skills/systematic-innovation/SKILL.md) is the sole editable source. Generated archives in `dist/` or GitHub Releases are release-only convenience distributions and are never committed to Git.
- **Byte-for-byte normalization:** [`tools/repository/package.py`](../tools/repository/package.py) builds deterministic ZIP distributions with:
  - Top-level prefix `systematic-innovation/` and sorted lexicographic POSIX paths;
  - Fixed UTC modification timestamp `1980-01-01T00:00:00Z`;
  - Normalized Unix file permissions `0644` and LF (`\n`) line endings;
  - `ZIP_DEFLATED` compression at `compresslevel=9`;
  - Explicit rejection of symlinks, path traversal, and any file outside the 5-file canonical allowlist (`SKILL.md` and `references/{deep-mode,evidence,innovation-lenses,output-contract}.md`).

---

## 2. Local Build and Install-From-Artifact Verification

To build and verify a reproducible distribution locally from a clean checkout:

```bash
# 1. Validate source isolation, authority routing, and skill format
python3 -m tools.repository validate

# 2. Build the canonical ZIP and release manifest
python3 -m tools.repository package \
  --source skills/systematic-innovation \
  --output dist/systematic-innovation.zip \
  --manifest dist/systematic-innovation.manifest.json \
  --version 0.1.0 \
  --revision "$(git rev-parse HEAD)"

# 3. Verify revocation denylist, manifest digests, canonical source rebuild,
#    and post-extraction installation smoke validation
python3 -m tools.repository verify-artifact \
  dist/systematic-innovation.zip \
  --manifest dist/systematic-innovation.manifest.json \
  --source skills/systematic-innovation \
  --revocations release/revocations.json \
  --policy release/policy.json
```

---

## 3. Verifying Public Releases (Origin Attestation vs. Checksum Integrity)

A SHA-256 digest (`systematic-innovation.zip.sha256` or `archive_sha256` in `systematic-innovation.manifest.json`) provides **integrity evidence only**, not proof of origin. Consumers must verify both:

1. **Revocation Denylist Check (First):**
   Ensure the artifact's SHA-256 digest is not listed in [`release/revocations.json`](../release/revocations.json) by running:
   ```bash
   python3 -m tools.repository verify-artifact systematic-innovation.zip \
     --manifest systematic-innovation.manifest.json \
     --revocations release/revocations.json \
     --policy release/policy.json
   ```
2. **GitHub Artifact Attestation (Origin Authenticity):**
   Verify that the ZIP archive was built by the trusted release workflow identity (`.github/workflows/release.yml` triggered on a `refs/tags/v*` SemVer tag):
   ```bash
   gh attestation verify systematic-innovation.zip \
     --repo poferraz/systematic-innovation \
     --signer-workflow poferraz/systematic-innovation/.github/workflows/release.yml
   ```
3. **SHA-256 Checksum Check:**
   ```bash
   shasum -a 256 -c systematic-innovation.zip.sha256
   ```

---

## 4. Trusted Workflow Identity & Identity Rotation

- **Trusted signer identity:** `.github/workflows/release.yml` executing on tag refs matching `^v[0-9]+\.[0-9]+\.[0-9]+$`, declared in [`release/policy.json`](../release/policy.json).
- **Identity rotation:** Any change to the release workflow path, attestation provider, or repository namespace requires a reviewed pull request updating `.github/workflows/release.yml`, `release/policy.json`, and this document together, recorded in [`CONTEXT.md`](../CONTEXT.md).

---

## 5. Artifact Revocation Procedure

Because cryptographic attestations are immutable once issued, a compromised, defective, or withdrawn release artifact must be revoked through the explicit denylist in [`release/revocations.json`](../release/revocations.json):

1. Add the withdrawn `archive_sha256` (and `payload_sha256` if applicable), `reason`, and `revoked_at` ISO date to `release/revocations.json` on `main`.
2. Mark the corresponding GitHub Release as withdrawn and remove its downloadable ZIP asset.
3. Publish a GitHub Security Advisory detailing the affected version, digest, and remediation.
4. `python3 -m tools.repository verify-artifact` checks `release/revocations.json` and rejects any listed digest with `REVOKED_ARTIFACT` even when its historical attestation remains cryptographically valid.
