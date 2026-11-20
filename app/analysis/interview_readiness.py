from typing import Dict, Any, List

def analyze_interview_readiness(features: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluates student interview preparation indicators based on communication assessments,
    presentation evidence, and soft skill practice records.
    """
    assessments = features.get("assessments", [])
    comm_assessments = [a["score"] for a in assessments if "communication" in a["type"].lower()]
    comm_score = round(sum(comm_assessments) / len(comm_assessments), 1) if comm_assessments else None

    student_skills = features.get("demonstrated_skills", {})
    mock_count = 0
    presentation_count = 0

    for sname, sdata in student_skills.items():
        for stype in sdata.get("source_types", []):
            if stype == "interview":
                mock_count += 1
            if "presentation" in sname.lower() or "presentation" in stype.lower():
                presentation_count += 1

    # Readiness level
    if comm_score is not None and comm_score >= 80 and mock_count >= 1:
        level = "Interview Ready"
    elif comm_score is not None and comm_score >= 60:
        level = "Basic Preparation Complete"
    elif mock_count > 0:
        level = "Practice Initiated"
    else:
        level = "Practice Required"

    # Recommended topics
    topics = []
    if comm_score is None or comm_score < 75:
        topics.append("STAR Method for Behavioral Interview Questions")
    if mock_count == 0:
        topics.append("Live Technical Problem Walkthrough & Thinking Aloud")
    topics.append("System Tradeoffs and Architecture Explanation")
    topics.append("Handling Edge Cases and Debugging Walkthroughs")

    return {
        "communication_score": comm_score,
        "mock_practices_count": mock_count,
        "presentation_evidence_count": presentation_count,
        "interview_readiness_level": level,
        "recommended_practice_topics": topics[:3]
    }
