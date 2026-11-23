# Project decisions

The project began with a question about Tudor Rickards’s *Stimulating Innovation: A Systems Approach* (1985). Could a structured conversation help an AI generate ideas that change a problem in genuinely different ways while preserving what already works? The book-to-skill project influenced the decision to make the method installable. The skill credits its sources and identifies the reasoning cells and output contracts developed for this project. [Source notes](skills/systematic-innovation/references/evidence.md) · [book-to-skill](https://github.com/virgiliojr94/book-to-skill)

## A portable skill and a separate benchmark

In September 2026 the owner approved a single editable Markdown skill. A host-specific adapter requires evidence that a host needs one. The benchmark and distribution tooling live outside the installable skill so contributors can change how they test or package it without introducing another version of its behavior. [Repository specification](docs/specifications/repository.md) · [Compatibility policy](compatibility/README.md)

## Restoring the original behavior

In October, a comparison found that the experimental skill batched discovery questions, changed its requested number of ideas and offered experiments automatically. The owner chose to restore the approved behavior. The skill now asks one discovery question at a time. The user decides which idea, if any, to pursue. Earlier outputs describe the candidate that generated them. [Finding and owner decision](evals/stress/contract-findings.md) · [Restored candidate evaluation](evals/restored-2026-10-18/report.md)

A later diagnostic found that the full portfolio could exceed a tight word limit. The compact format was revised and checked on the same development case. Those records support a bounded claim about the output format. [v2 diagnostic](evals/v2-loop/report.md)

## Study boundary

The owner approved offline readiness work for a proposed six-case feasibility study. The envelope is 70 generation requests, US$5 maximum and zero retries. The recorded approval leaves live execution pending. Human calibration, restricted validation, cross-agent comparisons and sealed testing require their own evidence before the project can report those results. [Readiness decision](benchmark/study/task9-readiness-approval.yaml) · [Stage gates](benchmark/study/stage-gates.yaml)
