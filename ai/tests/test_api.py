from fastapi.testclient import TestClient
from helly_ai.main import app

client = TestClient(app)

def test_query_skeleton():
    # Expect NotImplementedError until implementations exist
    resp = client.post("/v1/query", json={"question": "What should I discuss with Max?"})
    assert resp.status_code == 500

def test_ingest_skeleton():
    resp = client.post("/v1/ingest/member-corpus", json={
        "team_member_ref": "max",
        "items": [
            {"id": "1", "content": "Max did great", "created_at": "2024-01-01T00:00:00Z"}
        ]
    })
    assert resp.status_code == 500

