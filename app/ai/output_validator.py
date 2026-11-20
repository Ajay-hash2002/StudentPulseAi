from typing import Dict, Any, List, Tuple

def validate_ai_output(data: Any, allowed_skills: List[str]) -> Tuple[bool, str]:
    """
    Validates model output against schema and safety guardrails:
    - Must be a dictionary with required keys: summary, strengths, priority_gaps, actions, limitations
    - Allowed priority values: high, medium, low
    - Anti-hallucination check: checks that skills referenced exist in the grounded input
    """
    if not isinstance(data, dict):
        return False, "Output must be a JSON object"

    required_keys = {"summary", "strengths", "priority_gaps", "actions", "limitations"}
    if not required_keys.issubset(data.keys()):
        missing = required_keys - set(data.keys())
        return False, f"Missing required keys in AI response: {missing}"

    if not isinstance(data["summary"], str) or len(data["summary"].strip()) == 0:
        return False, "Summary must be a non-empty string"

    if not isinstance(data["strengths"], list):
        return False, "Strengths must be a list"

    if not isinstance(data["priority_gaps"], list):
        return False, "Priority gaps must be a list"

    if not isinstance(data["actions"], list):
        return False, "Actions must be a list"

    valid_priorities = {"high", "medium", "low"}
    for act in data["actions"]:
        if not isinstance(act, dict):
            return False, "Each action must be an object"
        if not {"title", "description", "priority", "reason"}.issubset(act.keys()):
            return False, "Action is missing required fields (title, description, priority, reason)"
        if act["priority"].lower() not in valid_priorities:
            return False, f"Invalid priority: {act['priority']}. Must be high, medium, or low"

    # Anti-hallucination guard: Verify mentioned skills
    allowed_skills_lower = {s.lower() for s in allowed_skills}
    for gap in data["priority_gaps"]:
        if isinstance(gap, dict) and "skill" in gap:
            skill_name = gap["skill"].strip().lower()
            if skill_name and skill_name not in allowed_skills_lower:
                return False, f"AI hallucination detected: skill '{gap['skill']}' was not present in supplied evidence."

    return True, "Valid"
