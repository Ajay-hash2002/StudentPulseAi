def test_t01_dashboard_with_valid_test_account(client, demo1_auth_headers):
    """T01: Open the dashboard with a valid test account -> loads correct profile."""
    response = client.get("/api/v1/students/me", headers=demo1_auth_headers)
    assert response.status_code == 200
    res_json = response.json()
    assert res_json["success"] is True
    assert res_json["data"]["student_id"] == "s-demo-001"
    assert "Aarav Sharma" in res_json["data"]["display_name"]
    assert res_json["data"]["email"] == "demo1@example.com"

def test_t02_incomplete_profile_form(client):
    """T02: Submit an incomplete profile / register form -> validation errors."""
    # Missing consent
    res1 = client.post("/api/v1/auth/register", json={
        "display_name": "Test Student",
        "email": "test@example.com",
        "password": "Password123",
        "consent_given": False
    })
    assert res1.status_code == 200
    assert res1.json()["success"] is False
    assert res1.json()["error"]["code"] == "CONSENT_REQUIRED"

    # Missing email / short password (Pydantic schema validation)
    res2 = client.post("/api/v1/auth/register", json={
        "display_name": "T",
        "email": "invalid-email",
        "password": "123",
        "consent_given": True
    })
    assert res2.status_code == 422
    assert res2.json()["success"] is False
    assert res2.json()["error"]["code"] == "VALIDATION_ERROR"

def test_t08_request_another_students_record(client, demo1_auth_headers, demo2_auth_headers):
    """T08: Request another student's record -> access denied (403 Forbidden)."""
    # Demo 2 tries to access Demo 1's action plan
    res = client.get("/api/v1/action-plans/plan_s-demo-001", headers=demo2_auth_headers)
    assert res.status_code == 403
    assert res.json()["success"] is False
    assert res.json()["error"]["code"] == "FORBIDDEN"

def test_login_flow(client):
    """Verify login with correct and incorrect credentials."""
    # Correct login
    res_ok = client.post("/api/v1/auth/login", json={
        "email": "demo1@example.com",
        "password": "Demo@12345"
    })
    assert res_ok.status_code == 200
    assert res_ok.json()["success"] is True
    assert "access_token" in res_ok.json()["data"]

    # Wrong password
    res_err = client.post("/api/v1/auth/login", json={
        "email": "demo1@example.com",
        "password": "WrongPassword"
    })
    assert res_err.status_code == 200
    assert res_err.json()["success"] is False
    assert res_err.json()["error"]["code"] == "INVALID_CREDENTIALS"
