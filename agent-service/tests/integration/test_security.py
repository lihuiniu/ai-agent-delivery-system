import pytest
from fastapi import status

def test_auth_failure():
    # No token
    response = client.post("/chat", json={"message": "test"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "WWW-Authenticate" in response.headers

    # Invalid token
    response = client.post(
        "/chat",
        json={"message": "test"},
        headers={"Authorization": "Bearer invalid"}
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN

@pytest.mark.parametrize("role", ["readonly", "guest"])
def test_role_based_access(role):
    token = generate_test_token(role)
    response = client.post(
        "/chat",
        json={"message": "change theme"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN