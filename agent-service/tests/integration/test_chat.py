import pytest
from fastapi.testclient import TestClient
from agent_service.main import app
import json

client = TestClient(app)

def test_streaming_response():
    with open('tests/api/test_data/conversation_payloads.json') as f:
        test_cases = json.load(f)
    
    for case_name, payload in test_cases.items():
        response = client.post(
            "/chat",
            json=payload,
            headers={"Authorization": "Bearer test_token"}
        )
        
        assert response.status_code == 200
        assert "text/event-stream" in response.headers["content-type"]
        
        # Verify streaming chunks
        chunks = []
        for chunk in response.iter_lines():
            if chunk:
                chunks.append(chunk.decode())
        
        assert len(chunks) > 0
        assert any("content" in c or "ACTION" in c for c in chunks)

def test_action_generation():
    with open('tests/api/test_data/expected_actions.json') as f:
        expected_actions = json.load(f)
    
    test_messages = {
        "theme": "Switch to dark mode",
        "notifications": "Enable email notifications"
    }
    
    for intent, message in test_messages.items():
        response = client.post(
            "/chat",
            json={"message": message},
            headers={"Authorization": "Bearer test_token"}
        )
        
        chunks = [c.decode() for c in response.iter_lines() if c]
        action_json = extract_action(chunks[-1])  # Last chunk should contain action
        
        expected = expected_actions[f"{intent}_{'dark' if intent == 'theme' else 'enable_email'}"]
        assert action_json["action_type"] == expected["action_type"]
        assert all(
            action_json["parameters"][k] == v 
            for k, v in expected["expected_params"].items()
        )

def extract_action(chunk: str) -> dict:
    """Extracts action JSON from stream chunk"""
    import re
    match = re.search(r'\{.*\}', chunk)
    return json.loads(match.group()) if match else {}