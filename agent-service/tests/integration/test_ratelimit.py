from fastapi.testclient import TestClient
import time

def test_rate_limiting():
    client = TestClient(app)
    
    # Burst test
    for i in range(11):  # Assuming 10 req/min limit
        response = client.post("/chat", json={"message": f"test {i}"})
        if i < 10:
            assert response.status_code == 200
        else:
            assert response.status_code == 429
            assert "Retry-After" in response.headers
    
    # Window test
    time.sleep(60)
    response = client.post("/chat", json={"message": "after window"})
    assert response.status_code == 200