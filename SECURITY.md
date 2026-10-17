# Security Policy

## Responsible Use of Agent Skills

`systematic-innovation` is a provider-neutral Agent Skill authored entirely in portable Markdown. It executes zero host binaries, makes zero network requests, and requires zero external Python dependencies at runtime.

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
2. Email the maintainers directly at `security@systematic-innovation.local` (or submit a private GitHub Security Advisory).
3. Include a minimal reproducible prompt, the host environment, and the observed failure mode.
