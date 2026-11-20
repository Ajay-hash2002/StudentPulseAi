from typing import Dict, Any, List
from app.analysis.skill_gap import get_role_by_id_or_title

def calculate_readiness_score(features: Dict[str, Any], role_identifier: str) -> Dict[str, Any]:
    """
    Computes a transparent, weighted readiness score with criterion breakdown
    and explicit limitations disclaimer.
    Readiness = (sum of achieved weighted criteria / sum of applicable criterion weights) * 100
    """
    role = get_role_by_id_or_title(role_identifier)
    if not role:
        raise ValueError(f"Role '{role_identifier}' not found in catalogue.")

    role_title = role["title"]
    required_skills = role.get("required_skills", [])
    student_skills = features.get("demonstrated_skills", {})
    assessments = features.get("assessments", [])
    project_skills = set(features.get("project_skills", []))

    # --- 1. Core Skills Match (Weight: 40.0) ---
    total_skill_weight = sum(r.get("weight", 1.0) for r in required_skills) or 1.0
    achieved_skill_points = 0.0
    demonstrated_req_count = 0

    for req in required_skills:
        sname = req["skill_name"]
        w = req.get("weight", 1.0)
        req_lvl = req.get("required_level", 2)
        if sname in student_skills:
            demonstrated_req_count += 1
            obs_lvl = student_skills[sname]["highest_level"]
            ratio = min(1.0, obs_lvl / req_lvl)
            achieved_skill_points += (w * ratio)

    core_skills_score = (achieved_skill_points / total_skill_weight) * 40.0

    # --- 2. Assessment Benchmark (Weight: 25.0) ---
    if assessments:
        avg_assessment = sum(a["score"] for a in assessments) / len(assessments)
        assessment_score = (avg_assessment / 100.0) * 25.0
        assessment_desc = f"Based on {len(assessments)} completed assessments (avg: {avg_assessment:.1f}%)."
    else:
        assessment_score = 0.0
        assessment_desc = "No assessments recorded yet. Submit technical or aptitude quizzes to activate."

    # --- 3. Project Portfolio Coverage (Weight: 20.0) ---
    req_names = [r["skill_name"] for r in required_skills]
    project_covered = [s for s in req_names if s in project_skills]
    if req_names:
        proj_ratio = len(project_covered) / len(req_names)
    else:
        proj_ratio = 0.0
    project_score = proj_ratio * 20.0
    project_desc = f"{len(project_covered)} of {len(req_names)} required skills demonstrated in practical projects."

    # --- 4. Interview Readiness & Soft Skills (Weight: 15.0) ---
    soft_skills = ["Communication", "Presentation", "Teamwork", "Problem Solving"]
    soft_demonstrated = [s for s in soft_skills if s in student_skills]
    has_interview_evidence = any(
        "interview" in student_skills.get(s, {}).get("source_types", [])
        for s in student_skills
    )
    soft_ratio = len(soft_demonstrated) / len(soft_skills)
    soft_bonus = 0.2 if has_interview_evidence else 0.0
    interview_score = min(15.0, (soft_ratio + soft_bonus) * 15.0)
    interview_desc = f"{len(soft_demonstrated)} soft skills verified" + (" (with interview evidence)." if has_interview_evidence else ".")

    # Total Score
    total_score = round(core_skills_score + assessment_score + project_score + interview_score, 1)
    evidence_coverage = round((demonstrated_req_count / len(required_skills) * 100.0), 1) if required_skills else 0.0

    # Qualitative Level
    if total_score >= 80:
        level = "High Readiness"
    elif total_score >= 60:
        level = "Moderate Readiness"
    elif total_score >= 35:
        level = "Foundation Stage"
    else:
        level = "Needs Baseline Evidence"

    # Identify top strengths and critical gaps
    strengths = []
    critical_gaps = []
    for req in required_skills:
        sname = req["skill_name"]
        if sname in student_skills and student_skills[sname]["highest_level"] >= req["required_level"]:
            strengths.append(f"{sname} (Level {student_skills[sname]['highest_level']})")
        elif sname not in student_skills:
            critical_gaps.append(f"{sname} (No evidence)")
        elif student_skills[sname]["highest_level"] < req["required_level"]:
            critical_gaps.append(f"{sname} (Level {student_skills[sname]['highest_level']} < {req['required_level']})")

    criteria = [
        {
            "criterion": "Core Role Skills Match",
            "weight": 40.0,
            "achieved_score": round(core_skills_score, 1),
            "max_possible": 40.0,
            "description": f"Verified proficiency on role competencies ({demonstrated_req_count}/{len(required_skills)} skills with evidence)."
        },
        {
            "criterion": "Assessment Benchmark",
            "weight": 25.0,
            "achieved_score": round(assessment_score, 1),
            "max_possible": 25.0,
            "description": assessment_desc
        },
        {
            "criterion": "Project Portfolio Evidence",
            "weight": 20.0,
            "achieved_score": round(project_score, 1),
            "max_possible": 20.0,
            "description": project_desc
        },
        {
            "criterion": "Interview & Soft-Skills Readiness",
            "weight": 15.0,
            "achieved_score": round(interview_score, 1),
            "max_possible": 15.0,
            "description": interview_desc
        }
    ]

    return {
        "target_role": role_title,
        "readiness_score": total_score,
        "evidence_coverage_pct": evidence_coverage,
        "readiness_level": level,
        "criteria_breakdown": criteria,
        "strengths": strengths[:4],
        "critical_gaps": critical_gaps[:5],
        "limitations": "This score is an indicator for guidance and personal development, not a judgement of a student's ability or future potential."
    }
