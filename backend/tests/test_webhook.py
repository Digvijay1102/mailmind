def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_webhook_missing_signature_headers(client):
    payload = {"from": "test@example.com", "subject": "Test", "text": "Hello"}
    response = client.post("/webhook", json=payload)
    assert response.status_code in [400, 401, 422]


def test_webhook_invalid_signature(client):
    payload = {"from": "test@example.com", "subject": "Test", "text": "Hello"}
    headers = {
        "svix-id": "fake-id-123",
        "svix-timestamp": "1234567890",
        "svix-signature": "v1,invalidsignature",
    }
    response = client.post("/webhook", json=payload, headers=headers)
    assert response.status_code in [400, 401]


def test_webhook_wrong_content_type(client):
    response = client.post(
        "/webhook",
        data="not json",
        headers={"Content-Type": "text/plain"},
    )
    assert response.status_code in [400, 401, 422]


def test_rules_endpoint_exists(client):
    response = client.get("/rules")
    assert response.status_code == 200


def test_hitl_endpoint_exists(client):
    response = client.get("/hitl")
    assert response.status_code == 200


def test_logs_endpoint_exists(client):
    response = client.get("/logs")
    assert response.status_code == 200