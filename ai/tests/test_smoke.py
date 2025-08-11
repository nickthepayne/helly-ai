from fastapi.testclient import TestClient
from helly_ai.main import app

def test_server_responds_404_on_unknown_route():
    client = TestClient(app)
    resp = client.get("/v1/unknown")
    assert resp.status_code == 404

