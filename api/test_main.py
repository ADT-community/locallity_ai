import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
import httpx
from main import app

client = TestClient(app)

@pytest.fixture
def mock_llm_response():
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = AsyncMock(
            status_code=200,
            json=lambda: {"choices": [{"message": {"content": "Habari yako?"}}]},
            raise_for_status=lambda: None
        )
        yield mock_post

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_chat_unsupported_language():
    response = client.post("/v1/chat", json={"lang": "xx-XX", "messages": [{"role": "user", "content": "Hello"}]})
    assert response.status_code == 400
    assert "Unsupported language" in response.json()["detail"]

def test_chat_empty_messages():
    response = client.post("/v1/chat", json={"lang": "sw-KE", "messages": []})
    assert response.status_code == 400
    assert "Messages cannot be empty" in response.json()["detail"]

def test_chat_success(mock_llm_response):
    with patch.dict("os.environ", {"LLM_API_URL": "http://mock-llm", "LLM_API_KEY": "test-key"}):
        response = client.post("/v1/chat", json={"lang": "sw-KE", "messages": [{"role": "user", "content": "Habari"}]})
        assert response.status_code == 200
        assert response.json() == {"reply": "Habari yako?"}
        
        # Verify the LLM was called with the correct system prompt
        call_args = mock_llm_response.call_args
        sent_json = call_args.kwargs["json"]
        assert sent_json["messages"][0]["role"] == "system"
        assert "sw-KE" in sent_json["messages"][0]["content"]

def test_chat_llm_error():
    with patch.dict("os.environ", {"LLM_API_URL": "http://mock-llm", "LLM_API_KEY": "test-key"}):
        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            mock_post.side_effect = httpx.ConnectError("Connection failed")
            response = client.post("/v1/chat", json={"lang": "sw-KE", "messages": [{"role": "user", "content": "Habari"}]})
            assert response.status_code == 502
            assert "Error communicating with LLM" in response.json()["detail"]
