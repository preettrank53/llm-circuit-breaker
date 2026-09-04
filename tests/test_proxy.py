import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
import httpx
from main import app, reset_tokens_used, init_db

@pytest.fixture(autouse=True)
def reset_db():
    init_db()
    reset_tokens_used()

def test_health_check():
    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

def test_streaming_rejection():
    with TestClient(app) as client:
        response = client.post("/v1/chat/completions", json={"stream": True})
        assert response.status_code == 400
        assert "Streaming is not supported" in response.json()["detail"]

@patch("httpx.AsyncClient.post", new_callable=AsyncMock)
def test_proxy_pass_through(mock_post):
    # Mock upstream response
    mock_response = httpx.Response(200, json={"usage": {"total_tokens": 10}, "choices": [{"message": {"content": "Hello!"}}]})
    mock_post.return_value = mock_response

    with TestClient(app) as client:
        # Initial request
        response = client.post("/v1/chat/completions", json={"model": "test", "messages": [{"role": "user", "content": "hi"}]})
        assert response.status_code == 200
        assert response.json()["choices"][0]["message"]["content"] == "Hello!"
        
        # Check budget updated
        budget_response = client.get("/v1/budget")
        assert budget_response.json()["tokens_used"] == 10

@patch("httpx.AsyncClient.post", new_callable=AsyncMock)
def test_429_rejection(mock_post):
    mock_response = httpx.Response(200, json={"usage": {"total_tokens": 110}, "choices": [{"message": {"content": "Exceeded!"}}]})
    mock_post.return_value = mock_response

    with TestClient(app) as client:
        # Use up budget (limit is 100)
        client.post("/v1/chat/completions", json={"model": "test", "messages": [{"role": "user", "content": "hi"}]})
        
        # Next request should be blocked
        response2 = client.post("/v1/chat/completions", json={"model": "test", "messages": [{"role": "user", "content": "hi"}]})
        assert response2.status_code == 429
        assert "Local Token Budget Exceeded" in response2.json()["detail"]
