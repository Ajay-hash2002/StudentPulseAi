import json
from pathlib import Path
from typing import Dict, Any, List
from app.config import settings

def load_action_catalogue() -> List[Dict[str, Any]]:
    """Loads approved actions from data/action_catalogue.json."""
    cat_file = settings.DATA_DIR / "action_catalogue.json"
    if not cat_file.exists():
        return []
    with open(cat_file, "r", encoding="utf-8") as f:
        data = json.load(f)
        return data.get("actions", [])

def generate_recommendations(gap_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Ranks and selects learning/practice actions from approved catalogue
    mapped directly to identified skill gaps.
    """
    catalogue = load_action_catalogue()
    actions_by_skill: Dict[str, List[Dict[str, Any]]] = {}
    for act in catalogue:
        sname = act.get("skill_name", "")
        actions_by_skill.setdefault(sname, []).append(act)

    role_title = gap_analysis.get("target_role", "Selected Goal")
    gaps = gap_analysis.get("gaps", [])

    candidates: List[Dict[str, Any]] = []

    for gap in gaps:
        status = gap.get("status")
        sname = gap.get("skill")
        req_lvl = gap.get("required_level")
        obs_lvl = gap.get("observed_level")

        if status in ("weak", "missing_evidence"):
            matching_actions = actions_by_skill.get(sname, [])
            
            # Priority weight calculation
            if status == "missing_evidence":
                priority = "high"
                priority_weight = 3
                reason = f"No verified evidence found for {sname}. Recommended to establish baseline proficiency for {role_title}."
            else:
                priority = "high" if req_lvl - (obs_lvl or 0) >= 2 else "medium"
                priority_weight = 2
                reason = f"Current observed level is below the required level for {sname}. Targeted practice will bridge this gap."

            if matching_actions:
                for act in matching_actions:
                    candidates.append({
                        "action_id": act.get("action_id"),
                        "action_text": f"{act.get('title')}: {act.get('description')}",
                        "skill_name": sname,
                        "priority": act.get("priority", priority),
                        "priority_weight": priority_weight,
                        "reason": reason,
                        "evidence_refs": gap.get("evidence_refs", ["Rule: Action Catalogue Match"]),
                        "estimated_effort": act.get("estimated_effort", "4-8 hours"),
                        "category": act.get("category", "Learning")
                    })
            else:
                # Fallback to structured standard action if catalog entry not specific
                candidates.append({
                    "action_id": f"act_custom_{sname.lower().replace(' ', '_')}",
                    "action_text": f"Complete hands-on project or assessment demonstrating {sname}",
                    "skill_name": sname,
                    "priority": priority,
                    "priority_weight": priority_weight,
                    "reason": reason,
                    "evidence_refs": gap.get("evidence_refs", ["Rule: Action Catalogue Fallback"]),
                    "estimated_effort": "6 hours",
                    "category": "Practice"
                })

    # Sort candidates by priority weight descending
    candidates.sort(key=lambda x: x["priority_weight"], reverse=True)
    return candidates
