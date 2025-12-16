from app.main import main_app
from fastapi.testclient import TestClient

test_client = TestClient(main_app)


def test_root_status_code():
    response = test_client.get("/api/v1/health")
    assert response.status_code == 200
