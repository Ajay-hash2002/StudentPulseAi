import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from app.config import settings

LEVEL_LABELS = {
    0: "Needs evidence / Unknown",
    1: "Beginner",
    2: "Basic",
    3: "Intermediate",
    4: "Advanced"
}

def load_role_requirements() -> Dict[str, Any]:
    """Loads versioned role requirements from data/role_requirements.json."""
    roles_file = settings.DATA_DIR / "role_requirements.json"
    if not roles_file.exists():
        return {"roles": []}
    with open(roles_file, "r", encoding="utf-8") as f:
        return json.load(f)

def get_role_by_id_or_title(role_identifier: str) -> Optional[Dict[str, Any]]:
    data = load_role_requirements()
    target_clean = role_identifier.strip().lower()
    for r in data.get("roles", []):
        if r.get("role_id", "").lower() == target_clean or r.get("title", "").lower() == target_clean:
            return r
    # Fallback to first role if not matched
    return data["roles"][0] if data.get("roles") else None

def analyze_skill_gaps(features: Dict[str, Any], role_identifier: str) -> Dict[str, Any]:
    """
    Compares student demonstrated skills against target role requirements.
    Missing evidence is explicitly flagged as 'missing_evidence' / 'Needs evidence / Unknown'.
    """
    role = get_role_by_id_or_title(role_identifier)
    if not role:
        raise ValueError(f"Role definition '{role_identifier}' not found in role catalogue.")

    role_title = role["title"]
    required_skills = role.get("required_skills", [])
    student_skills = features.get("demonstrated_skills", {})

    gaps: List[Dict[str, Any]] = []
    strong_count = 0
    weak_count = 0
    missing_count = 0

    for req in required_skills:
        sname = req["skill_name"]
        req_level = req["required_level"]

        if sname in student_skills:
            obs_level = student_skills[sname]["highest_level"]
            ev_ids = student_skills[sname]["evidence_ids"]
            ev_refs = student_skills[sname]["references"]

            if obs_level >= req_level:
                status = "strong"
                strong_count += 1
                reason = f"Demonstrated {LEVEL_LABELS.get(obs_level, 'Level ' + str(obs_level))} meets or exceeds the required {LEVEL_LABELS.get(req_level)}."
            else:
                status = "weak"
                weak_count += 1
                reason = f"Demonstrated {LEVEL_LABELS.get(obs_level, 'Level ' + str(obs_level))} is below the required {LEVEL_LABELS.get(req_level)}."

            gaps.append({
                "skill": sname,
                "required_level": req_level,
                "observed_level": obs_level,
                "level_label": LEVEL_LABELS.get(obs_level, "Unknown"),
                "status": status,
                "reason": reason,
                "evidence_refs": ev_refs if ev_refs else [f"Evidence record: {ev_ids[0]}"]
            })
        else:
            status = "missing_evidence"
            missing_count += 1
            gaps.append({
                "skill": sname,
                "required_level": req_level,
                "observed_level": None,
                "level_label": "Needs evidence / Unknown",
                "status": "missing_evidence",
                "reason": f"No verified evidence provided for {sname}. Target requirement is {LEVEL_LABELS.get(req_level)}.",
                "evidence_refs": ["No evidence submitted"]
            })

    return {
        "target_role": role_title,
        "total_required_skills": len(required_skills),
        "strong_count": strong_count,
        "weak_count": weak_count,
        "missing_count": missing_count,
        "gaps": gaps
    }
