from typing import Dict, Any, List
from app.analysis.skill_gap import get_role_by_id_or_title

def analyze_project_readiness(features: Dict[str, Any], role_identifier: str) -> Dict[str, Any]:
    """
    Evaluates student's project portfolio against required role skills.
    Returns coverage percentage, demonstrated skills, and missing capabilities.
    """
    role = get_role_by_id_or_title(role_identifier)
    if not role:
        raise ValueError(f"Role '{role_identifier}' not found.")

    role_title = role["title"]
    required_skills = [r["skill_name"] for r in role.get("required_skills", [])]
    project_skills = set(features.get("project_skills", []))
    completed_projects_count = features.get("completed_projects_count", 0)

    demonstrated = [s for s in required_skills if s in project_skills]
    missing = [s for s in required_skills if s not in project_skills]

    coverage_pct = round((len(demonstrated) / len(required_skills) * 100.0), 1) if required_skills else 0.0

    if coverage_pct >= 70:
        summary = "Strong project portfolio covering major architectural and technical requirements."
    elif coverage_pct >= 40:
        summary = "Moderate project evidence; key role competencies demonstrated, but some technical gaps remain."
    else:
        summary = "Limited practical project evidence for this target role. Hands-on projects recommended."

    return {
        "target_role": role_title,
        "completed_projects_count": completed_projects_count,
        "demonstrated_skills": demonstrated,
        "missing_role_capabilities": missing,
        "project_coverage_pct": coverage_pct,
        "readiness_summary": summary
    }
