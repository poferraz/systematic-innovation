# Security Policy

## Responsible Use of Agent Skills

`systematic-innovation` is a provider-neutral Agent Skill authored entirely in portable Markdown. It executes zero host binaries, makes zero network requests, and requires zero external Python dependencies at runtime.

### Repository Trust Zones

The repository maintains strict trust boundaries across three distinct zones:

1. **Public Skill (`skills/systematic-innovation/`):** Pure-Markdown public agent skill. Contains zero host binaries, makes zero network requests, requires zero runtime dependencies, and stores zero credentials.
2. **Tooling and Asset Generation (`tools/`, `tests/`):** Executable Python tooling, static test harnesses, and dev-only Playwright asset generation. These tools are used exclusively for repository validation, benchmarking, and documentation asset generation; they are never packaged or shipped inside the canonical skill directory.
3. **Restricted Datasets and Local Sources (`sources/`, `restricted/`):** Local source materials (`sources/`) and restricted evaluation or sealed-test packs (`restricted/`, `*.restricted.*`, `*.validation.yaml`, `*.sealed.yaml`). These assets are strictly excluded from public Git tracking, CI pipelines, and generated release distributions.

### 1. Inspecting Skill Content Before Installation

Because Agent Skills execute instructions within your LLM's system prompt or tool context, always audit skill content before installing or activating it in production environments:
- Verify that the skill contains only Markdown documentation and schema references.
- Confirm that no executable scripts (`.sh`, `.exe`, `.py` CLI runners) or background daemons are packaged in the skill directory.
- Verify that file paths within the skill do not escape the skill directory root via path traversal (`../..`).

### 2. Protecting Credentials and Sensitive Data

- **Never place credentials in prompts:** Do not include API tokens, database connection strings, passwords, or personal identifiable information (PII) in ideation challenges, discovery responses, or evaluation datasets.
- **Benchmark isolation:** Ensure that all benchmark runs and pilot evaluation logs (`evals/pilot/results/`, `benchmark/runs/`) are scrubbed of private keys or sensitive proprietary business logic before committing to public repositories.

### 3. Reporting False Attribution and Vulnerabilities

If you discover a security vulnerability, an instruction injection vector, or false attribution / hallucinated academic references within the repository:
1. Do not open a public issue.
2. Submit a private GitHub Security Advisory via the repository's Security tab (choose "Report a vulnerability").
3. Include a minimal reproducible prompt, the host environment, and the observed failure mode.
