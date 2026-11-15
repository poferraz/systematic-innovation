"""Observable format checks, kept separate from semantic quality judgments."""
from __future__ import annotations

import re

from ..models import Job, ResponseRecord


def score_deterministic(job: Job, response: ResponseRecord) -> dict[str, float | int | bool | None]:
    if response.job_id != job.job_id:
        raise ValueError('response correlation mismatch')
    final = response.conversation.final_response if response.conversation else response.content
    assistant_texts = ([t.content for t in response.conversation.turns if t.role == 'assistant']
                       if response.conversation else [response.content])
    requested = re.search(r'\b(\d+)\s+(?:ideas|options|possibilities|mechanisms)\b', job.prompt, re.IGNORECASE)
    return {'succeeded': response.status == 'succeeded', 'output_present': bool(final.strip()),
                'candidate_count': len(re.findall(r'^\s*P\d+:', final, re.MULTILINE)),
                'requested_count': int(requested[1]) if requested else None,
                'question_count': sum(text.count('?') for text in assistant_texts),
                'implementation_drift': bool(re.search(r'\b(?:week\s+\d+|rollout plan|implementation roadmap|budget allocation)\b', final, re.IGNORECASE)),
                'final_response_output_tokens': (response.conversation.final_response_output_tokens
                                              if response.conversation else response.output_tokens),
                'total_assistant_output_tokens': response.total_assistant_output_tokens,
                'assistant_turn_count': len(assistant_texts),
                'latency_seconds': response.conversation.total_latency_seconds if response.conversation else response.latency_seconds,
                'cost': response.conversation.total_cost if response.conversation else response.cost}
