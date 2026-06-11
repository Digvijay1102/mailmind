import pytest


@pytest.fixture
def sample_rule():
    return {
        "name": "Invoice Rule",
        "description": "Handle all invoice emails",
        "intent_match": "invoice",
        "urgency_min": 5,
        "action_type": "label",
        "action_value": "invoices",
        "require_hitl": False,
    }


# ── CREATE ────────────────────────────────────────────────────────────────────

def test_create_rule(client, sample_rule):
    response = client.post("/rules", json=sample_rule)
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert isinstance(data["id"], int)


def test_create_rule_missing_required_field(client):
    incomplete = {"name": "Bad Rule"}
    response = client.post("/rules", json=incomplete)
    assert response.status_code == 422


# ── LIST ──────────────────────────────────────────────────────────────────────

def test_list_rules_empty(client):
    response = client.get("/rules")
    assert response.status_code == 200
    assert response.json() == []


def test_list_rules_returns_created_rule(client, sample_rule):
    client.post("/rules", json=sample_rule)
    response = client.get("/rules")
    assert response.status_code == 200
    rules = response.json()
    assert len(rules) == 1
    assert rules[0]["name"] == "Invoice Rule"
    assert rules[0]["intent_match"] == "invoice"
    assert rules[0]["action_type"] == "label"


def test_list_rules_multiple(client, sample_rule):
    client.post("/rules", json=sample_rule)
    sample_rule["name"] = "Spam Rule"
    sample_rule["intent_match"] = "spam"
    client.post("/rules", json=sample_rule)
    response = client.get("/rules")
    assert len(response.json()) == 2


# ── UPDATE ────────────────────────────────────────────────────────────────────

def test_update_rule(client, sample_rule):
    create_resp = client.post("/rules", json=sample_rule)
    rule_id = create_resp.json()["id"]
    update_resp = client.put(f"/rules/{rule_id}", json={"name": "Updated Invoice Rule"})
    assert update_resp.status_code == 200
    assert update_resp.json()["status"] == "updated"
    rules = client.get("/rules").json()
    assert rules[0]["name"] == "Updated Invoice Rule"


def test_update_nonexistent_rule(client):
    response = client.put("/rules/99999", json={"name": "Ghost Rule"})
    assert response.status_code == 404
    assert response.json()["detail"] == "Rule not found"


# ── DELETE ────────────────────────────────────────────────────────────────────

def test_delete_rule(client, sample_rule):
    create_resp = client.post("/rules", json=sample_rule)
    rule_id = create_resp.json()["id"]
    delete_resp = client.delete(f"/rules/{rule_id}")
    assert delete_resp.status_code == 200
    assert delete_resp.json()["status"] == "deleted"
    rules = client.get("/rules").json()
    assert len(rules) == 0


def test_delete_nonexistent_rule(client):
    response = client.delete("/rules/99999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Rule not found"