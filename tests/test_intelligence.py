from app.analysis.profile_features import extract_profile_features
from app.analysis.skill_gap import analyze_skill_gaps
from app.analysis.readiness import calculate_readiness_score
from app.analysis.recommendations import generate_recommendations
from tests.conftest import TestingSessionLocal

def test_t04_skill_gap_analysis_with_sufficient_evidence(client, demo1_auth_headers):
    """T04: Run skill-gap analysis with sufficient evidence -> returns strong/weak gaps and reasons."""
    payload = {"target_role": "Backend Developer"}
    response = client.post("/api/v1/analysis/skill-gaps", json=payload, headers=demo1_auth_headers)
    assert response.status_code == 200
    res_json = response.json()
    assert res_json["success"] is True
    data = res_json["data"]
    assert data["target_role"] == "Backend Developer"
    assert data["strong_count"] > 0
    # Python should be strong for Demo 1
    python_gap = next((g for g in data["gaps"] if g["skill"] == "Python"), None)
    assert python_gap is not None
    assert python_gap["status"] == "strong"
    assert python_gap["observed_level"] >= python_gap["required_level"]
    assert len(python_gap["reason"]) > 0

def test_t05_skill_gap_analysis_with_missing_evidence(client, demo3_auth_headers):
    """T05: Run analysis with missing evidence -> system labels information as missing/unknown, not assumed."""
    payload = {"target_role": "Data Analyst"}
    response = client.post("/api/v1/analysis/skill-gaps", json=payload, headers=demo3_auth_headers)
    assert response.status_code == 200
    res_json = response.json()
    assert res_json["success"] is True
    data = res_json["data"]
    # Demo 3 has zero evidence -> all required skills must be labeled missing_evidence
    assert data["missing_count"] == data["total_required_skills"]
    assert data["strong_count"] == 0
    for g in data["gaps"]:
        assert g["status"] == "missing_evidence"
        assert g["observed_level"] is None
        assert g["level_label"] == "Needs evidence / Unknown"
        assert "No verified evidence" in g["reason"]

def test_t06_generate_action_plan(client, demo1_auth_headers):
    """T06: Generate an action plan -> actions are relevant to identified gaps and include reasons."""
    payload = {"target_role": "Backend Developer"}
    response = client.post("/api/v1/action-plans", json=payload, headers=demo1_auth_headers)
    assert response.status_code == 200
    res_json = response.json()
    assert res_json["success"] is True
    data = res_json["data"]
    assert data["target_role"] == "Backend Developer"
    assert len(data["actions"]) > 0
    for act in data["actions"]:
        assert act["priority"] in ["high", "medium", "low"]
        assert len(act["action_text"]) > 0
        assert len(act["reason"]) > 0

def test_t12_recommendation_traceability(client, demo1_auth_headers):
    """T12: Check recommendation traceability -> each recommendation can be linked to evidence or a documented rule."""
    payload = {"target_role": "Backend Developer"}
    response = client.post("/api/v1/action-plans", json=payload, headers=demo1_auth_headers)
    assert response.status_code == 200
    actions = response.json()["data"]["actions"]
    for act in actions:
        assert "evidence_refs" in act
        assert isinstance(act["evidence_refs"], list)
        assert len(act["evidence_refs"]) > 0

def test_readiness_formula_and_breakdown(test_db):
    """Verify transparent weighted readiness score formula correctness."""
    # Check Demo 1 (Rich profile)
    features1 = extract_profile_features(test_db, "s-demo-001")
    readiness1 = calculate_readiness_score(features1, "Backend Developer")
    assert readiness1["readiness_score"] > 60.0
    assert readiness1["evidence_coverage_pct"] > 60.0
    assert len(readiness1["criteria_breakdown"]) == 4

    # Check Demo 3 (Fresh/Empty profile)
    features3 = extract_profile_features(test_db, "s-demo-003")
    readiness3 = calculate_readiness_score(features3, "Data Analyst")
    assert readiness3["readiness_score"] == 0.0
    assert readiness3["evidence_coverage_pct"] == 0.0
    assert readiness3["readiness_level"] == "Needs Baseline Evidence"
    assert "not a judgement" in readiness3["limitations"].lower()
