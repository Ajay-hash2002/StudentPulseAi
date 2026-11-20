from app.ai.output_validator import validate_ai_output
from app.ai.ai_explainer import generate_deterministic_explanation

def test_t09_simulate_ai_fallback_and_validation():
    """T09: Simulate AI provider timeout or invalid JSON -> system shows safe fallback and does not crash."""
    # Test valid fallback structure
    mock_gap_analysis = {
        "target_role": "Backend Developer",
        "strong_count": 2,
        "weak_count": 1,
        "missing_count": 1,
        "gaps": [
            {"skill": "Python", "status": "strong", "reason": "Demonstrated Level 3"},
            {"skill": "FastAPI", "status": "weak", "reason": "Level 1 vs required 3"},
            {"skill": "Docker", "status": "missing_evidence", "reason": "No evidence"}
        ]
    }
    mock_readiness = {
        "readiness_score": 65.0,
        "readiness_level": "Moderate Readiness",
        "evidence_coverage_pct": 75.0
    }
    mock_actions = [
        {"action_id": "act_fastapi", "skill_name": "FastAPI", "action_text": "Build CRUD API with FastAPI", "priority": "high", "reason": "Bridge gap"}
    ]

    fallback = generate_deterministic_explanation(mock_gap_analysis, mock_readiness, mock_actions)
    assert fallback is not None
    assert "summary" in fallback
    assert len(fallback["actions"]) > 0

    valid, msg = validate_ai_output(fallback, ["Python", "FastAPI", "Docker"])
    assert valid is True

    # Test hallucination detection: AI hallucinates a skill not in the provided facts
    hallucinated_output = {
        "summary": "Sample summary",
        "strengths": [],
        "priority_gaps": [{"skill": "Quantum Computing", "reason": "Not learned"}],
        "actions": [{"title": "Learn QC", "description": "Physics", "priority": "high", "reason": "Reason"}],
        "limitations": ["None"]
    }
    valid_h, msg_h = validate_ai_output(hallucinated_output, ["Python", "FastAPI", "Docker"])
    assert valid_h is False
    assert "hallucination detected" in msg_h
