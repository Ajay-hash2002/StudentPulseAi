import json
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.database.models import Student, StudentSkillEvidence, Assessment, Project, Certification, Skill

def extract_profile_features(db: Session, student_id: str) -> Dict[str, Any]:
    """
    Extracts and normalizes raw evidence, assessments, projects, and certifications
    into analysis-ready features for a given student.
    """
    # 1. Fetch skill evidence
    evidence_records = (
        db.query(StudentSkillEvidence, Skill.skill_name)
        .join(Skill, StudentSkillEvidence.skill_id == Skill.skill_id)
        .filter(StudentSkillEvidence.student_id == student_id)
        .all()
    )

    skill_features: Dict[str, Dict[str, Any]] = {}
    for ev, skill_name in evidence_records:
        if skill_name not in skill_features:
            skill_features[skill_name] = {
                "highest_level": ev.observed_level,
                "evidence_ids": [ev.evidence_id],
                "references": [ev.evidence_reference],
                "source_types": [ev.source_type],
                "latest_date": ev.date
            }
        else:
            if ev.observed_level > skill_features[skill_name]["highest_level"]:
                skill_features[skill_name]["highest_level"] = ev.observed_level
            skill_features[skill_name]["evidence_ids"].append(ev.evidence_id)
            skill_features[skill_name]["references"].append(ev.evidence_reference)
            skill_features[skill_name]["source_types"].append(ev.source_type)
            if ev.date > skill_features[skill_name]["latest_date"]:
                skill_features[skill_name]["latest_date"] = ev.date

    # 2. Fetch assessments
    assessments = db.query(Assessment).filter(Assessment.student_id == student_id).all()
    assessment_scores = [a.score_or_result for a in assessments]
    avg_assessment = sum(assessment_scores) / len(assessment_scores) if assessment_scores else None

    # 3. Fetch projects
    projects = db.query(Project).filter(Project.student_id == student_id).all()
    project_skills = set()
    for p in projects:
        try:
            skills_list = json.loads(p.skills_used)
            if isinstance(skills_list, list):
                project_skills.update([s.strip() for s in skills_list])
        except Exception:
            pass

    # 4. Fetch certifications
    certifications = db.query(Certification).filter(Certification.student_id == student_id).all()

    return {
        "student_id": student_id,
        "demonstrated_skills": skill_features,
        "assessments": [
            {
                "id": a.assessment_id,
                "type": a.assessment_type,
                "score": a.score_or_result,
                "max_score": a.max_score
            } for a in assessments
        ],
        "average_assessment_score": avg_assessment,
        "projects_count": len(projects),
        "completed_projects_count": len([p for p in projects if p.status == "completed"]),
        "project_skills": list(project_skills),
        "certifications_count": len(certifications),
        "certifications": [c.name for c in certifications]
    }
