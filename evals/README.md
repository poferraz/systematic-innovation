# Evaluation evidence

The pilot, stress tests and later comparison runs record what the skill produced for fixed cases. Each run can include its own prompts, answers, model, usage and measurement inputs. These are needed to interpret the results. The [October reproduction guide](restored-2026-10-18/runbook.md) explains how to recompute its summaries without calling a model.

## Public copies

The archived records use portable paths for command binaries, checkout files and temporary outputs. Session identifiers and tool-event identifiers have local labels, and the pilot identifies conversations by condition, case and replicate. The published files omit completed resume checkpoints. Each removed checkpoint had the same prompt digest, model and turns as one retained result.

The cleanup compared all 478 JSONL records with the preceding revision, `15312d2`. Prompts, answers, token counts, latency and scores matched. Where an integrity or provenance file cited a changed run file, its SHA-256 now checks the public copy. The earlier revision retains the original byte digests. Freeze files keep the input and scoring-code digests recorded at the time of each study.
