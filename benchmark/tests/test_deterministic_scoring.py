from datetime import UTC, datetime

from systematic_innovation_bench.models import (
    Condition,
    ConversationRecord,
    ConversationTurn,
    Job,
    ResponseRecord,
)
from systematic_innovation_bench.scoring.deterministic import score_deterministic


def test_unknown_tokens_remain_missing_and_questions_are_observed():
    job = Job(run_id='r', case_id='a', condition=Condition.VANILLA, replicate=0, model='m', host='h',
              prompt='Give 2 ideas', created_at=datetime.now(UTC))
    score = score_deterministic(job, ResponseRecord(job_id=job.job_id, status='succeeded',
                                                   content='What constraint? What else?'))
    assert score['total_assistant_output_tokens'] is None
    assert score['question_count'] == 2
    assert score['requested_count'] == 2
    assert score['output_present'] is True


def test_multi_turn_scores_final_portfolio_but_counts_all_questions_and_tokens():
    job = Job(run_id='r', case_id='a', condition=Condition.VANILLA, replicate=0, model='m', host='h',
              prompt='Give ideas', created_at=datetime.now(UTC))
    turns = (ConversationTurn(turn_index=1, role='user', content='Options?'),
             ConversationTurn(turn_index=2, role='assistant', content='Who benefits?', output_tokens=800),
             ConversationTurn(turn_index=3, role='user', content='People. Final portfolio'),
             ConversationTurn(turn_index=4, role='assistant', content='P1: first\nP2: second', output_tokens=1200))
    convo = ConversationRecord(job_id=job.job_id, turns=turns, turn_response_ids=('a','b'),
                               final_response=turns[-1].content, final_response_output_tokens=1200,
                               total_assistant_output_tokens=2000, total_latency_seconds=4)
    response = ResponseRecord(job_id=job.job_id, status='succeeded', conversation=convo)
    score = score_deterministic(job, response)
    assert score['candidate_count'] == 2
    assert score['question_count'] == 1
    assert score['final_response_output_tokens'] == 1200
    assert score['total_assistant_output_tokens'] == 2000
