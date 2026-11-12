from fastapi.testclient import TestClient
from rag_assistant.main import app

client = TestClient(app)

def test_health():
    assert client.get("/health").json() == {"status": "ok"}

def test_empty_knowledge_base_answer():
    response = client.post("/api/v1/ask", json={"question": "What does the guide say?"})
    assert response.status_code == 200
    assert response.json()["sources"] == []
    assert "couldn't find" in response.json()["answer"]
