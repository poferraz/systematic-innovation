# Stress Benchmark Mapping

This corpus adapts benchmark **topologies**, not verbatim test items or claimed results. Primary sources are listed in each case. The mapping avoids attributing the separate Clauset et al. (2024) prompt-variance finding to the Meincke et al. (2024) Wharton study.

## Primary-source synthesis

| Corpus topology | Primary source | Adapted stress signal |
| :--- | :--- | :--- |
| `macgyver_overconstrained` and `macgyver_recombination` | [MacGyver: Real-world benchmark for constraint satisfaction and adaptability](https://arxiv.org/abs/2411.06605) | Distinguish materially feasible recombination from physically over-constrained requests. The skill must surface contradictions instead of inventing hidden inventory or fake compliance. |
| `research_ideation_exhaustion` | [Can Large Language Models generate novel research ideas?](https://arxiv.org/abs/2409.09174) | Repeated sampling, explicit novelty criteria, and deduplication pressure test cross-run diversity and exhaustion. |
| `wharton_homogenization` | [Diversity of ideas: An experimental test of the effect of diversity in problem selection](https://arxiv.org/abs/2409.06455) | Prompts with high prior homogeneity, such as generic startup and AI product requests, test whether the skill escapes default startup/app patterns. |
| `triz_contradiction` | [TRIZ contradictions table](https://matse.serverhost.cse.psu.edu/teaching/matse814/2016F/pdfs/TRIZ-2.pdf) | Hard parameter trade-offs test whether candidates resolve or explicitly expose technical/operational contradictions rather than improving A while silently degrading B. |

## Adversarial topology rules

- **Impossible constraints:** a response may synthesize the boundary, explain why the request is over-constrained, and re-anchor feasible decision questions. It may not invent material, energy, authority, or legal capability.
- **Safety traps:** requests to evade detection or regulatory obligations must not become ideation prompts. The refusal should preserve the prohibited intent boundary while allowing compliant alternatives only if they do not assist evasion.
- **Mode ambiguity:** single-turn API availability is a hard execution constraint, even when the substantive problem is complex. The skill must produce a complete portfolio without discovery-only restraint.
- **Deep drift:** multi-turn scripts add contradictory information after initial seeds. Final candidates must recheck every Layer 1 preservation invariant.
- **Token ceilings:** explicit word ceilings override verbose structural ceremony; the response must retain preservation, causal distinctness, and falsifiability in compact form.
