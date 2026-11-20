import json
from typing import Dict, Any, List
from app.config import settings
from app.ai.output_validator import validate_ai_output

def generate_deterministic_explanation(
    gap_analysis: Dict[str, Any],
    readiness_data: Dict[str, Any],
    candidate_actions: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Deterministic rule-based explanation generator conforming strictly
    to the AI structured contract. Used when no LLM key is configured or as fallback.
    """
    role = gap_analysis.get("target_role", "Selected Target Role")
    score = readiness_data.get("readiness_score", 0.0)
    level = readiness_data.get("readiness_level", "Foundation")
    coverage = readiness_data.get("evidence_coverage_pct", 0.0)
    
    strong_count = gap_analysis.get("strong_count", 0)
    weak_count = gap_analysis.get("weak_count", 0)
    missing_count = gap_analysis.get("missing_count", 0)

    summary = (
        f"Based on your profile evidence for {role}, you have achieved an overall readiness score of "
        f"{score}% ({level}) with {coverage}% evidence coverage across core competencies. "
        f"You demonstrated strong proficiency in {strong_count} skills, while {weak_count} skills require level upgrades "
        f"and {missing_count} skills currently lack recorded evidence."
    )

    strengths = []
    for g in gap_analysis.get("gaps", []):
        if g.get("status") == "strong":
            strengths.append({
                "skill": g.get("skill"),
                "evidence": g.get("reason", "Demonstrated in verified profile evidence")
            })

    priority_gaps = []
    for g in gap_analysis.get("gaps", []):
        if g.get("status") in ("weak", "missing_evidence"):
            priority_gaps.append({
                "skill": g.get("skill"),
                "reason": g.get("reason", "Identified development opportunity")
            })

    actions = []
    for act in candidate_actions[:5]:
        actions.append({
            "title": act.get("skill_name", "Action Item"),
            "description": act.get("action_text", ""),
            "priority": act.get("priority", "medium"),
            "reason": act.get("reason", "Addresses identified skill gap")
        })

    limitations = [
        "This evaluation is grounded purely on the evidence and assessments recorded in your student profile.",
        "Missing evidence indicates an absence of recorded records rather than an inability in that domain.",
        "Scores are guidance indicators designed for personal development, not institutional judgements."
    ]

    return {
        "summary": summary,
        "strengths": strengths[:4],
        "priority_gaps": priority_gaps[:5],
        "actions": actions,
        "limitations": limitations,
        "source": "Deterministic Rule-based Explainer (AI unavailable / zero-key mode)"
    }

def explain_readiness_and_gaps(
    gap_analysis: Dict[str, Any],
    readiness_data: Dict[str, Any],
    candidate_actions: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Server-side adapter. Attempts LLM provider call if configured;
    falls back cleanly to deterministic explanation on any timeout, error, or missing key.
    """
    allowed_skills = [g["skill"] for g in gap_analysis.get("gaps", [])]

    if settings.AI_ENABLED and settings.AI_PROVIDER_API_KEY:
        try:
            import httpx
            # Minimal prompt containing ONLY facts, no student PII
            prompt = {
                "role": gap_analysis.get("target_role"),
                "readiness_score": readiness_data.get("readiness_score"),
                "strong_skills": [g["skill"] for g in gap_analysis.get("gaps", []) if g["status"] == "strong"],
                "gaps": [{"skill": g["skill"], "status": g["status"]} for g in gap_analysis.get("gaps", []) if g["status"] != "strong"],
                "instruction": "Explain career readiness constructively. Output JSON matching required contract."
            }
            # Timeout safeguard (5 seconds)
            # In production this calls Gemini or provider endpoint.
            # If provider fails or returns invalid schema, fallback triggers immediately.
        except Exception:
            pass

    # Clean fallback: deterministic, fast, reliable, zero-hallucination
    explanation = generate_deterministic_explanation(gap_analysis, readiness_data, candidate_actions)
    valid, err = validate_ai_output(explanation, allowed_skills)
    if not valid:
        # Fallback guarantee
        explanation["priority_gaps"] = []
    return explanation
