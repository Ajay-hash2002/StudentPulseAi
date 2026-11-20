import json
import uuid
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from app.config import settings
from app.database.models import Student, Skill, StudentSkillEvidence, Assessment, Project, Certification, CareerGoal
from app.services.auth_service import hash_password

def seed_database(db: Session):
    """Seed synthetic skills and 3 demo profiles with varied evidence richness."""
    now = datetime.now(timezone.utc)

    # 1. Seed Skills if not present
    if db.query(Skill).count() == 0:
        skills_data = [
            # Technical
            ("skill_python", "Python", "General-purpose high-level programming language", "Technical"),
            ("skill_sql", "SQL", "Structured query language for relational database management", "Technical"),
            ("skill_fastapi", "FastAPI", "Modern high-performance web framework for Python APIs", "Technical"),
            ("skill_rest_apis", "REST APIs", "RESTful web services and API design principles", "Technical"),
            ("skill_dsa", "Data Structures", "Fundamental memory organization (lists, trees, graphs, heaps)", "Technical"),
            ("skill_algo", "Algorithms", "Algorithmic problem-solving, sorting, and complexity", "Technical"),
            ("skill_oop", "OOP", "Object-Oriented Programming principles and design patterns", "Technical"),
            ("skill_js", "JavaScript", "Client and server web programming language", "Technical"),
            ("skill_html_css", "HTML/CSS", "Web markup and responsive styling specifications", "Technical"),
            ("skill_react", "React", "Declarative component-based UI library", "Technical"),
            ("skill_pandas", "Pandas", "Data manipulation and analysis library for Python", "Technical"),
            ("skill_stats", "Statistics", "Probability distributions, statistical hypothesis testing", "Technical"),
            ("skill_ml", "Machine Learning", "Supervised and unsupervised predictive algorithms", "Technical"),
            ("skill_data_viz", "Data Visualization", "Information presentation using charts and dashboards", "Technical"),
            ("skill_sys_design", "System Design", "Scalable distributed architecture design", "Technical"),
            ("skill_testing", "Testing", "Unit, integration, and contract test automation", "Technical"),
            ("skill_docker", "Docker", "Containerization and local virtualization", "Technical"),
            ("skill_linux", "Linux", "Unix shell scripting and server administration", "Technical"),
            ("skill_cloud", "Cloud Basics", "Fundamentals of cloud storage, compute, and serverless", "Technical"),
            ("skill_git", "Git", "Distributed version control and branch workflows", "Tools"),
            ("skill_postman", "Postman", "API testing and automated endpoint validation", "Tools"),
            
            # Soft Skills
            ("skill_comm", "Communication", "Clear verbal and written technical communication", "Soft"),
            ("skill_presentation", "Presentation", "Technical presenting and demonstration delivery", "Soft"),
            ("skill_teamwork", "Teamwork", "Collaborative problem-solving and peer code reviews", "Soft"),
            ("skill_problem_solving", "Problem Solving", "Analytical reasoning and debugging methodologies", "Soft"),
        ]
        
        for sid, sname, sdesc, scat in skills_data:
            skill = Skill(skill_id=sid, skill_name=sname, description=sdesc, category=scat)
            db.add(skill)
        db.commit()

    # 2. Check if demo students exist
    if db.query(Student).filter(Student.email == "demo1@example.com").first():
        return

    # Skill mapping lookup
    skills_map = {s.skill_name: s.skill_id for s in db.query(Skill).all()}
    demo_password_hash = hash_password("Demo@12345")

    # DEMO 1: Rich Profile (Aarav Sharma) -> Backend Developer
    s1_id = "s-demo-001"
    student1 = Student(
        student_id=s1_id,
        display_name="Aarav Sharma (Demo - Rich)",
        email="demo1@example.com",
        password_hash=demo_password_hash,
        consent_given=True,
        consent_at=now - timedelta(days=30),
        created_at=now - timedelta(days=30)
    )
    db.add(student1)

    # Goal
    db.add(CareerGoal(
        goal_id=str(uuid.uuid4()),
        student_id=s1_id,
        target_role="Backend Developer",
        target_date="2027-06-30",
        notes="Aiming for backend engineer placement at top tech firm."
    ))

    # Evidence for Demo 1
    s1_evidence = [
        ("Python", "assessment", "Python Advanced Quiz (Score: 92/100)", 3),
        ("FastAPI", "project", "Built RESTful API with auth and SQLite", 3),
        ("SQL", "assessment", "Database Design & SQL Test (Score: 88/100)", 3),
        ("REST APIs", "project", "Designed OpenAPI-compliant endpoints", 3),
        ("Data Structures", "assessment", "DSA Midterm Test (Score: 85/100)", 3),
        ("Algorithms", "assessment", "Algorithms Benchmark (Score: 78/100)", 2),
        ("Git", "project", "Maintained GitHub team repo with 45+ commits", 2),
        ("Testing", "project", "Wrote 18 pytest unit tests for backend API", 2),
        ("Communication", "interview", "Technical Mock Interview - Verbal Rating A-", 3),
        ("Problem Solving", "assessment", "Analytical Aptitude Test (Score: 88/100)", 3),
    ]
    for sname, stype, sref, slevel in s1_evidence:
        if sname in skills_map:
            db.add(StudentSkillEvidence(
                student_id=s1_id,
                skill_id=skills_map[sname],
                source_type=stype,
                evidence_reference=sref,
                observed_level=slevel,
                date=now - timedelta(days=15)
            ))

    # Assessments for Demo 1
    db.add(Assessment(student_id=s1_id, assessment_type="Python Quiz", score_or_result=92.0, max_score=100.0, completed_at=now - timedelta(days=20)))
    db.add(Assessment(student_id=s1_id, assessment_type="DSA Test", score_or_result=85.0, max_score=100.0, completed_at=now - timedelta(days=18)))
    db.add(Assessment(student_id=s1_id, assessment_type="Aptitude", score_or_result=88.0, max_score=100.0, completed_at=now - timedelta(days=12)))
    db.add(Assessment(student_id=s1_id, assessment_type="Communication", score_or_result=90.0, max_score=100.0, completed_at=now - timedelta(days=10)))

    # Projects for Demo 1
    db.add(Project(
        student_id=s1_id,
        title="E-Commerce REST API Engine",
        description="Scalable backend with JWT authentication, cart checkout, and SQLite database.",
        skills_used=json.dumps(["Python", "FastAPI", "SQL", "REST APIs", "Testing"]),
        status="completed"
    ))
    db.add(Project(
        student_id=s1_id,
        title="Student Pulse AI Prototype",
        description="Career readiness analyzer using FastAPI and transparent Python intelligence rules.",
        skills_used=json.dumps(["Python", "FastAPI", "Git", "REST APIs"]),
        status="in_progress"
    ))

    # Certification for Demo 1
    db.add(Certification(
        student_id=s1_id,
        name="Python for Everybody Specialization",
        issuer="Coursera / University of Michigan",
        issue_date=now - timedelta(days=60),
        verification_reference="CERT-PY-98421"
    ))

    # DEMO 2: Sparse Profile (Priya Patel) -> Full-Stack Developer
    s2_id = "s-demo-002"
    student2 = Student(
        student_id=s2_id,
        display_name="Priya Patel (Demo - Sparse)",
        email="demo2@example.com",
        password_hash=demo_password_hash,
        consent_given=True,
        consent_at=now - timedelta(days=14),
        created_at=now - timedelta(days=14)
    )
    db.add(student2)

    db.add(CareerGoal(
        goal_id=str(uuid.uuid4()),
        student_id=s2_id,
        target_role="Full-Stack Developer",
        target_date="2027-12-31",
        notes="Exploring frontend and backend web development."
    ))

    s2_evidence = [
        ("HTML/CSS", "project", "Designed responsive static portfolio page", 2),
        ("JavaScript", "self_reported", "Completed beginner JS exercises", 1),
    ]
    for sname, stype, sref, slevel in s2_evidence:
        if sname in skills_map:
            db.add(StudentSkillEvidence(
                student_id=s2_id,
                skill_id=skills_map[sname],
                source_type=stype,
                evidence_reference=sref,
                observed_level=slevel,
                date=now - timedelta(days=7)
            ))

    db.add(Assessment(student_id=s2_id, assessment_type="Python Quiz", score_or_result=65.0, max_score=100.0, completed_at=now - timedelta(days=5)))
    db.add(Project(
        student_id=s2_id,
        title="Personal Portfolio Website",
        description="Responsive static site featuring bio and coursework achievements.",
        skills_used=json.dumps(["HTML/CSS", "JavaScript"]),
        status="completed"
    ))

    # DEMO 3: Fresh / Empty Profile (Rohan Verma) -> Data Analyst
    s3_id = "s-demo-003"
    student3 = Student(
        student_id=s3_id,
        display_name="Rohan Verma (Demo - Empty)",
        email="demo3@example.com",
        password_hash=demo_password_hash,
        consent_given=True,
        consent_at=now - timedelta(days=2),
        created_at=now - timedelta(days=2)
    )
    db.add(student3)

    db.add(CareerGoal(
        goal_id=str(uuid.uuid4()),
        student_id=s3_id,
        target_role="Data Analyst",
        target_date="2027-08-15",
        notes="Interested in SQL and business analytics."
    ))
    # Zero evidence records, zero projects, zero assessments to show clean missing-evidence handling

    db.commit()
