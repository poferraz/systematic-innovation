# Systematic Innovation

![Systematic Innovation](assets/banner.png)

Systematic Innovation is a Markdown skill for people who ask an AI for ideas and get variations of the same answer. Give it a problem, a constraint and something that already works. It proposes options, explains how each would change the situation and identifies what each should preserve.

## Try it

Use a host that supports the Agent Skills standard. Copy the complete [skill directory](skills/systematic-innovation/) into a skills directory recognized by your host. For a Codex project, run these commands from its root:

```sh
git clone https://github.com/poferraz/systematic-innovation.git
mkdir -p .agents/skills
cp -R systematic-innovation/skills/systematic-innovation .agents/skills/
```

In a new session, ask for example, “Use Systematic Innovation. Our repair café has a queue at opening time. Volunteers can’t add another shift. What are some ways to shorten the wait while keeping walk-ins welcome?” Hosts with manual instruction loading can use the [skill entry point](skills/systematic-innovation/SKILL.md) and its adjacent references.

**Quick Mode** returns options in one turn. **Deep Mode** asks about the problem and its constraints before generating options. **Piped Compact** fits a short word budget. The method asks the model to set aside the obvious answers and examine different mechanisms. The skill calls this “Negative-Space Trope Quarantine.” [Reasoning lenses](skills/systematic-innovation/references/innovation-lenses.md) · [Method diagram](assets/v2-anti-collapse-loop.svg) · [Short output example](assets/v2-piped-budget-lock.svg)

## My role and what changed

I chose to keep a single portable skill that people can use across hosts, with separate tooling to test it. When an experimental revision started offering implementation steps automatically, I chose to restore the original rule. The person asking for ideas decides whether to take an option further. AI tools helped implement the skill and generate evaluation samples. [Project decisions](CONTEXT.md) · [Recorded correction](evals/stress/contract-findings.md)

The method draws on Tudor Rickards’s *Stimulating Innovation: A Systems Approach* (1985). The project designed its own reasoning cells and output format. [Sources and attribution](skills/systematic-innovation/references/evidence.md)

## What the evidence shows

A development test asked for a portfolio in at most 350 words. The earlier skill produced 494 and 569 words. With the revised compact format, two later runs on the same case produced 286 and 289 words. These were bounded checks on one model. Independent human ratings of usefulness and a cross-model comparison are pending. [Evaluation report](evals/v2-loop/report.md) · [Earlier study and limitations](evals/restored-2026-10-18/report.md)

Version 2.0.0 also received 100/100 in the keyless SkillEvaluator check. This measures the properties that the static evaluator checks. [Static audit](evals/audits/2026-11-14-skillevaluator-final.md)

## Repository guide

| Directory | What you will find |
| --- | --- |
| [Skill](skills/systematic-innovation/) | The installable Markdown instructions and references |
| [Benchmark](benchmark/README.md) | The separate Python runner, public cases and an offline example |
| [Evaluations](evals/) | Samples and reports supporting the observations above |
| [Specifications](docs/specifications/) | The skill, evaluation and repository contracts |

Run `python3 -m unittest discover tests -v` from the repository root to check the skill and tooling. The benchmark has its own locked environment. [Contributor checks](AGENTS.md) · [Security](SECURITY.md) · [MIT license](LICENSE)
