"""One-turn offline exchange fixture. No network or provider dependency."""
import json
import sys

job = json.load(sys.stdin)
print(json.dumps({'job_id': job['job_id'], 'turn_index': job['assistant_turn_index'], 'attempt': job['attempt'],
    'content': 'P1: Shared slots | Intervention: queue | Lever: pool demand | Chain: tasks -> shared slots -> less delay',
    'input_tokens': 10,'output_tokens': 100,'cost': 0.01,'latency_seconds': 0.01}))
