def test_t03_valid_assessment_submit(client, demo1_auth_headers):
    """T03: Submit a valid assessment result -> assessment is saved and returned correctly."""
    payload = {
        "assessment_type": "System Design Evaluation",
        "score_or_result": 82.5,
        "max_score": 100.0
    }
    response = client.post("/api/v1/assessments", json=payload, headers=demo1_auth_headers)
    assert response.status_code == 200
    res_json = response.json()
    assert res_json["success"] is True
    assert res_json["data"]["assessment_type"] == "System Design Evaluation"
    assert res_json["data"]["score_or_result"] == 82.5

    # Check listing
    list_res = client.get("/api/v1/assessments", headers=demo1_auth_headers)
    assert list_res.status_code == 200
    items = list_res.json()["data"]
    assert any(a["assessment_type"] == "System Design Evaluation" for a in items)

def test_t07_invalid_api_payload(client, demo1_auth_headers):
    """T07: Send an invalid API payload -> returns controlled 422 validation error."""
    # Score exceeds max_score bounds or wrong types
    payload = {
        "assessment_type": "Python",
        "score_or_result": 150.0  # Constraint: ge=0, le=100
    }
    response = client.post("/api/v1/assessments", json=payload, headers=demo1_auth_headers)
    assert response.status_code == 422
    res_json = response.json()
    assert res_json["success"] is False
    assert res_json["error"]["code"] == "VALIDATION_ERROR"
    assert "request_id" in res_json
