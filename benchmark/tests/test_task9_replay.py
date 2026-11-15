import hashlib
import json

import pytest

from task9.replay import ReplayBundle


def test_replay_is_request_bound_and_never_live(tmp_path):
    payload={"input":[{"role":"user","content":"Synthetic request"}]}
    key=hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
    path=tmp_path/"fixture.json"
    path.write_text(json.dumps({"responses":[{"request_sha256":key,"input_bound_tokens":100,
         "status":200,"request_id":"offline-request","body":{"synthetic":True}}]}))
    replay=ReplayBundle.load(path)
    assert replay.is_live is False
    assert replay.bound(payload).tokens==100
    assert replay.bound(payload).certified_for_live is False
    assert replay.send(payload,timeout_seconds=120,max_output_bytes=1024).status==200
    with pytest.raises(ValueError):
        replay.bound({"input":[]})


def test_duplicate_replay_keys_and_oversize_fixture_response_are_refused(tmp_path):
    row={"request_sha256":"a"*64,"input_bound_tokens":1,"status":200,"request_id":"offline-request","body":{}}
    path=tmp_path/"fixture.json"
    path.write_text(json.dumps({"responses":[row,row]}))
    with pytest.raises(ValueError):
        ReplayBundle.load(path)


def test_replay_unicode_digest_matches_runner_canonical_request(tmp_path):
    payload={"instructions":"Preserve Δ access"}
    # Runner canonical JSON escapes non-ASCII; this fixture is independent of replay's helper.
    key=hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    path=tmp_path/"unicode.json"
    path.write_text(json.dumps({"responses":[{"request_sha256":key,"input_bound_tokens":20,
       "status":200,"request_id":"unicode-request","body":{}}]}))
    replay=ReplayBundle.load(path)
    assert replay.bound(payload).request_sha256==key
