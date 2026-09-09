# seed.py
import bcrypt
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models.course import Course, CategoryEnum
from app.models.degree_requirement import DegreeRequirement
from app.models.student_course import StudentCourse, StatusEnum
from app.models.user import User

DATABASE_URL = "sqlite:///./app.db"  # change to your actual DB URL

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)

Base.metadata.create_all(bind=engine)


def seed():
    db = SessionLocal()

    # ── Courses ───────────────────────────────────────────────────────────────
    courses = [
        # CS Core
        Course(code="CSCI 10100", name="Introduction to Computing", credits=3, category=CategoryEnum.core, is_cs_elective_eligible=False),
        Course(code="CSCI 12700", name="Introduction to Computer Science", credits=3, category=CategoryEnum.core, is_cs_elective_eligible=True, prereq_description="High school math", min_grade_required="C"),
        Course(code="CSCI 21000", name="Data Structures", credits=3, category=CategoryEnum.core, is_cs_elective_eligible=True, prereq_description="CSCI 12700", min_grade_required="C"),
        Course(code="CSCI 22000", name="Discrete Structures", credits=3, category=CategoryEnum.core, is_cs_elective_eligible=True, prereq_description="CSCI 12700"),
        Course(code="CSCI 26500", name="Computer Organization", credits=3, category=CategoryEnum.core, is_cs_elective_eligible=True, prereq_description="CSCI 21000"),
        Course(code="CSCI 33500", name="Software Analysis and Design I", credits=3, category=CategoryEnum.core, is_cs_elective_eligible=True, prereq_description="CSCI 21000", min_grade_required="C"),
        Course(code="CSCI 34300", name="Software Analysis and Design II", credits=3, category=CategoryEnum.core, is_cs_elective_eligible=True, prereq_description="CSCI 33500", min_grade_required="C"),
        Course(code="CSCI 30100", name="Theory of Computation", credits=3, category=CategoryEnum.core, is_cs_elective_eligible=True, prereq_description="CSCI 22000"),
        Course(code="CSCI 32000", name="Computer Architecture", credits=3, category=CategoryEnum.core, is_cs_elective_eligible=True, prereq_description="CSCI 26500"),

        # CS Focus Study
        Course(code="CSCI 31500", name="Software Engineering", credits=3, category=CategoryEnum.focus_study, is_cs_elective_eligible=True, prereq_description="CSCI 33500"),
        Course(code="CSCI 36000", name="Principles of Programming Languages", credits=3, category=CategoryEnum.focus_study, is_cs_elective_eligible=True, prereq_description="CSCI 22000"),
        Course(code="CSCI 37000", name="Algorithms", credits=3, category=CategoryEnum.focus_study, is_cs_elective_eligible=True, prereq_description="CSCI 21000 and CSCI 22000"),
        Course(code="CSCI 38000", name="Operating Systems", credits=3, category=CategoryEnum.focus_study, is_cs_elective_eligible=True, prereq_description="CSCI 26500"),
        Course(code="CSCI 39000", name="Computer Networks", credits=3, category=CategoryEnum.focus_study, is_cs_elective_eligible=True),
        Course(code="CSCI 39500", name="Distributed Systems", credits=3, category=CategoryEnum.focus_study, is_cs_elective_eligible=True, prereq_description="CSCI 39000"),
        Course(code="CSCI 38500", name="Compilers", credits=3, category=CategoryEnum.focus_study, is_cs_elective_eligible=True, prereq_description="CSCI 36000"),
        Course(code="CSCI 37500", name="Computer Security", credits=3, category=CategoryEnum.focus_study, is_cs_elective_eligible=True, prereq_description="CSCI 38000"),

        # CS Electives
        Course(code="CSCI 40100", name="Machine Learning", credits=3, category=CategoryEnum.elective, is_cs_elective_eligible=True, prereq_description="CSCI 37000"),
        Course(code="CSCI 41000", name="Artificial Intelligence", credits=3, category=CategoryEnum.elective, is_cs_elective_eligible=True, prereq_description="CSCI 37000"),
        Course(code="CSCI 42000", name="Computer Graphics", credits=3, category=CategoryEnum.elective, is_cs_elective_eligible=True),
        Course(code="CSCI 43000", name="Database Systems", credits=3, category=CategoryEnum.elective, is_cs_elective_eligible=True, prereq_description="CSCI 33500"),
        Course(code="CSCI 44000", name="Cybersecurity", credits=3, category=CategoryEnum.elective, is_cs_elective_eligible=True),
        Course(code="CSCI 44500", name="Cloud Computing", credits=3, category=CategoryEnum.elective, is_cs_elective_eligible=True, prereq_description="CSCI 39000"),
        Course(code="CSCI 45000", name="Deep Learning", credits=3, category=CategoryEnum.elective, is_cs_elective_eligible=True, prereq_description="CSCI 40100"),
        Course(code="CSCI 45500", name="Natural Language Processing", credits=3, category=CategoryEnum.elective, is_cs_elective_eligible=True, prereq_description="CSCI 40100"),
        Course(code="CSCI 46000", name="Computer Vision", credits=3, category=CategoryEnum.elective, is_cs_elective_eligible=True, prereq_description="CSCI 40100"),
        Course(code="CSCI 46500", name="Blockchain and Decentralized Systems", credits=3, category=CategoryEnum.elective, is_cs_elective_eligible=True),
        Course(code="CSCI 47000", name="Mobile Application Development", credits=3, category=CategoryEnum.elective, is_cs_elective_eligible=True, prereq_description="CSCI 33500"),
        Course(code="CSCI 47500", name="Web Development", credits=3, category=CategoryEnum.elective, is_cs_elective_eligible=True, prereq_description="CSCI 33500"),
        Course(code="CSCI 48000", name="Game Development", credits=3, category=CategoryEnum.elective, is_cs_elective_eligible=True, prereq_description="CSCI 42000"),
        Course(code="CSCI 48500", name="Human-Computer Interaction", credits=3, category=CategoryEnum.elective, is_cs_elective_eligible=True),
        Course(code="CSCI 49000", name="Robotics", credits=3, category=CategoryEnum.elective, is_cs_elective_eligible=True, prereq_description="CSCI 40100"),
        Course(code="CSCI 49500", name="Quantum Computing", credits=3, category=CategoryEnum.elective, is_cs_elective_eligible=True, prereq_description="CSCI 30100"),

        # Math
        Course(code="MATH 20100", name="Calculus I", credits=4, category=CategoryEnum.general, is_cs_elective_eligible=False),
        Course(code="MATH 20200", name="Calculus II", credits=4, category=CategoryEnum.general, is_cs_elective_eligible=False, prereq_description="MATH 20100"),
        Course(code="MATH 32700", name="Linear Algebra", credits=3, category=CategoryEnum.general, is_cs_elective_eligible=False, prereq_description="MATH 20100"),
        Course(code="MATH 34600", name="Probability and Statistics", credits=3, category=CategoryEnum.general, is_cs_elective_eligible=False, prereq_description="MATH 20100"),
        Course(code="MATH 39200", name="Discrete Mathematics", credits=3, category=CategoryEnum.general, is_cs_elective_eligible=False),
        Course(code="MATH 30100", name="Multivariable Calculus", credits=4, category=CategoryEnum.general, is_cs_elective_eligible=False, prereq_description="MATH 20200"),
        Course(code="MATH 45000", name="Numerical Methods", credits=3, category=CategoryEnum.general, is_cs_elective_eligible=False, prereq_description="MATH 32700"),

        # English / Communication
        Course(code="ENGL 10100", name="English Composition I", credits=3, category=CategoryEnum.general, is_cs_elective_eligible=False),
        Course(code="ENGL 21000", name="Technical Writing", credits=3, category=CategoryEnum.general, is_cs_elective_eligible=False),
        Course(code="ENGL 22000", name="Business Writing", credits=3, category=CategoryEnum.general, is_cs_elective_eligible=False),
        Course(code="COMM 10100", name="Public Speaking", credits=3, category=CategoryEnum.general, is_cs_elective_eligible=False),
        Course(code="COMM 30100", name="Professional Communication", credits=3, category=CategoryEnum.general, is_cs_elective_eligible=False),

        # Humanities / Social Sciences
        Course(code="PHIL 10100", name="Ethics in Technology", credits=3, category=CategoryEnum.general, is_cs_elective_eligible=False),
        Course(code="PHIL 20200", name="Logic and Critical Thinking", credits=3, category=CategoryEnum.general, is_cs_elective_eligible=False),
        Course(code="HIST 10100", name="History of Science and Technology", credits=3, category=CategoryEnum.general, is_cs_elective_eligible=False),
        Course(code="HIST 20100", name="Modern World History", credits=3, category=CategoryEnum.general, is_cs_elective_eligible=False),
        Course(code="SOCY 10100", name="Introduction to Sociology", credits=3, category=CategoryEnum.general, is_cs_elective_eligible=False),
        Course(code="PSYC 10100", name="Introduction to Psychology", credits=3, category=CategoryEnum.general, is_cs_elective_eligible=False),
        Course(code="ECON 10100", name="Introduction to Economics", credits=3, category=CategoryEnum.general, is_cs_elective_eligible=False),
        Course(code="POLS 10100", name="Introduction to Political Science", credits=3, category=CategoryEnum.general, is_cs_elective_eligible=False),

        # Sciences
        Course(code="PHYS 20700", name="Physics I", credits=4, category=CategoryEnum.general, is_cs_elective_eligible=False, prereq_description="MATH 20100"),
        Course(code="PHYS 20800", name="Physics II", credits=4, category=CategoryEnum.general, is_cs_elective_eligible=False, prereq_description="PHYS 20700"),
    ]

    db.add_all(courses)
    db.commit()
    for c in courses:
        db.refresh(c)

    course_map = {c.code: c for c in courses}

    # ── Degree Requirements ───────────────────────────────────────────────────
    requirements = [
        DegreeRequirement(name="Computer Science", credits_required=120, category_filter=CategoryEnum.core, notes="Bachelor of Science in Computer Science"),
        DegreeRequirement(name="General Studies", credits_required=60, category_filter=CategoryEnum.general, notes="Associate degree in General Studies"),
    ]
    db.add_all(requirements)
    db.commit()

    # ── Users ─────────────────────────────────────────────────────────────────
    def hash_pw(pw: str) -> bytes:
        return bcrypt.hashpw(pw.encode(), bcrypt.gensalt())

    users = [
        User(name="Admin", email="admin@admin.com", hashed_password=hash_pw("admin"), college="CCNY", major="Computer Science", degree_type="BS"),
        User(name="John Doe", email="john@example.com", hashed_password=hash_pw("secret123"), college="CCNY", major="Computer Science", degree_type="BS"),
        User(name="Jane Smith", email="jane@example.com", hashed_password=hash_pw("secret123"), college="CCNY", major="Computer Science", degree_type="BS"),
        User(name="Bob Lee", email="bob@example.com", hashed_password=hash_pw("secret123"), college="CCNY", major="General Studies", degree_type="AS"),
    ]
    db.add_all(users)
    db.commit()
    for u in users:
        db.refresh(u)

    admin, john, jane, bob = users

    # ── Student Courses ───────────────────────────────────────────────────────
    enrollments = [
        # Admin — senior, almost done
        StudentCourse(user_id=admin.id, course_id=course_map["CSCI 10100"].id, status=StatusEnum.completed, semester="Fall 2020", grade="A", grade_points=4.0, credits_applied=3),
        StudentCourse(user_id=admin.id, course_id=course_map["CSCI 12700"].id, status=StatusEnum.completed, semester="Fall 2020", grade="A", grade_points=4.0, credits_applied=3),
        StudentCourse(user_id=admin.id, course_id=course_map["CSCI 21000"].id, status=StatusEnum.completed, semester="Spring 2021", grade="A-", grade_points=3.7, credits_applied=3),
        StudentCourse(user_id=admin.id, course_id=course_map["CSCI 22000"].id, status=StatusEnum.completed, semester="Spring 2021", grade="B+", grade_points=3.3, credits_applied=3),
        StudentCourse(user_id=admin.id, course_id=course_map["CSCI 26500"].id, status=StatusEnum.completed, semester="Fall 2021", grade="A", grade_points=4.0, credits_applied=3),
        StudentCourse(user_id=admin.id, course_id=course_map["CSCI 33500"].id, status=StatusEnum.completed, semester="Fall 2021", grade="A-", grade_points=3.7, credits_applied=3),
        StudentCourse(user_id=admin.id, course_id=course_map["CSCI 34300"].id, status=StatusEnum.completed, semester="Spring 2022", grade="B+", grade_points=3.3, credits_applied=3),
        StudentCourse(user_id=admin.id, course_id=course_map["CSCI 37000"].id, status=StatusEnum.completed, semester="Spring 2022", grade="A", grade_points=4.0, credits_applied=3),
        StudentCourse(user_id=admin.id, course_id=course_map["CSCI 38000"].id, status=StatusEnum.completed, semester="Fall 2022", grade="B+", grade_points=3.3, credits_applied=3),
        StudentCourse(user_id=admin.id, course_id=course_map["CSCI 40100"].id, status=StatusEnum.completed, semester="Fall 2022", grade="A", grade_points=4.0, credits_applied=3),
        StudentCourse(user_id=admin.id, course_id=course_map["CSCI 43000"].id, status=StatusEnum.completed, semester="Spring 2023", grade="A-", grade_points=3.7, credits_applied=3),
        StudentCourse(user_id=admin.id, course_id=course_map["MATH 20100"].id, status=StatusEnum.completed, semester="Fall 2020", grade="A", grade_points=4.0, credits_applied=4),
        StudentCourse(user_id=admin.id, course_id=course_map["MATH 20200"].id, status=StatusEnum.completed, semester="Spring 2021", grade="A-", grade_points=3.7, credits_applied=4),
        StudentCourse(user_id=admin.id, course_id=course_map["MATH 32700"].id, status=StatusEnum.completed, semester="Fall 2021", grade="B+", grade_points=3.3, credits_applied=3),
        StudentCourse(user_id=admin.id, course_id=course_map["ENGL 10100"].id, status=StatusEnum.completed, semester="Fall 2020", grade="A", grade_points=4.0, credits_applied=3),
        StudentCourse(user_id=admin.id, course_id=course_map["ENGL 21000"].id, status=StatusEnum.completed, semester="Spring 2021", grade="A-", grade_points=3.7, credits_applied=3),
        StudentCourse(user_id=admin.id, course_id=course_map["PHIL 10100"].id, status=StatusEnum.completed, semester="Fall 2021", grade="B+", grade_points=3.3, credits_applied=3),
        StudentCourse(user_id=admin.id, course_id=course_map["PHYS 20700"].id, status=StatusEnum.completed, semester="Spring 2022", grade="B", grade_points=3.0, credits_applied=4),
        StudentCourse(user_id=admin.id, course_id=course_map["CSCI 45000"].id, status=StatusEnum.in_progress, semester="Fall 2023", credits_applied=3),
        StudentCourse(user_id=admin.id, course_id=course_map["CSCI 44500"].id, status=StatusEnum.in_progress, semester="Fall 2023", credits_applied=3),
        StudentCourse(user_id=admin.id, course_id=course_map["CSCI 49000"].id, status=StatusEnum.planned),
        StudentCourse(user_id=admin.id, course_id=course_map["CSCI 49500"].id, status=StatusEnum.planned),

        # John — junior
        StudentCourse(user_id=john.id, course_id=course_map["CSCI 10100"].id, status=StatusEnum.completed, semester="Fall 2022", grade="A", grade_points=4.0, credits_applied=3),
        StudentCourse(user_id=john.id, course_id=course_map["CSCI 12700"].id, status=StatusEnum.completed, semester="Fall 2022", grade="A-", grade_points=3.7, credits_applied=3),
        StudentCourse(user_id=john.id, course_id=course_map["CSCI 21000"].id, status=StatusEnum.completed, semester="Spring 2023", grade="B+", grade_points=3.3, credits_applied=3),
        StudentCourse(user_id=john.id, course_id=course_map["CSCI 22000"].id, status=StatusEnum.completed, semester="Spring 2023", grade="B", grade_points=3.0, credits_applied=3),
        StudentCourse(user_id=john.id, course_id=course_map["MATH 20100"].id, status=StatusEnum.completed, semester="Fall 2022", grade="A", grade_points=4.0, credits_applied=4),
        StudentCourse(user_id=john.id, course_id=course_map["MATH 20200"].id, status=StatusEnum.completed, semester="Spring 2023", grade="B+", grade_points=3.3, credits_applied=4),
        StudentCourse(user_id=john.id, course_id=course_map["ENGL 10100"].id, status=StatusEnum.completed, semester="Fall 2022", grade="A-", grade_points=3.7, credits_applied=3),
        StudentCourse(user_id=john.id, course_id=course_map["CSCI 26500"].id, status=StatusEnum.in_progress, semester="Fall 2023", credits_applied=3),
        StudentCourse(user_id=john.id, course_id=course_map["CSCI 33500"].id, status=StatusEnum.in_progress, semester="Fall 2023", credits_applied=3),
        StudentCourse(user_id=john.id, course_id=course_map["PHIL 10100"].id, status=StatusEnum.planned),
        StudentCourse(user_id=john.id, course_id=course_map["CSCI 37000"].id, status=StatusEnum.planned),

        # Jane — sophomore
        StudentCourse(user_id=jane.id, course_id=course_map["CSCI 10100"].id, status=StatusEnum.completed, semester="Fall 2023", grade="B+", grade_points=3.3, credits_applied=3),
        StudentCourse(user_id=jane.id, course_id=course_map["ENGL 10100"].id, status=StatusEnum.completed, semester="Fall 2023", grade="A", grade_points=4.0, credits_applied=3),
        StudentCourse(user_id=jane.id, course_id=course_map["MATH 20100"].id, status=StatusEnum.in_progress, semester="Spring 2024", credits_applied=4),
        StudentCourse(user_id=jane.id, course_id=course_map["CSCI 12700"].id, status=StatusEnum.in_progress, semester="Spring 2024", credits_applied=3),
        StudentCourse(user_id=jane.id, course_id=course_map["PHIL 10100"].id, status=StatusEnum.planned),
        StudentCourse(user_id=jane.id, course_id=course_map["CSCI 21000"].id, status=StatusEnum.planned),

        # Bob — general studies
        StudentCourse(user_id=bob.id, course_id=course_map["ENGL 10100"].id, status=StatusEnum.completed, semester="Fall 2022", grade="A", grade_points=4.0, credits_applied=3),
        StudentCourse(user_id=bob.id, course_id=course_map["ENGL 21000"].id, status=StatusEnum.completed, semester="Spring 2023", grade="B", grade_points=3.0, credits_applied=3),
        StudentCourse(user_id=bob.id, course_id=course_map["HIST 10100"].id, status=StatusEnum.completed, semester="Fall 2022", grade="B+", grade_points=3.3, credits_applied=3),
        StudentCourse(user_id=bob.id, course_id=course_map["SOCY 10100"].id, status=StatusEnum.completed, semester="Spring 2023", grade="A-", grade_points=3.7, credits_applied=3),
        StudentCourse(user_id=bob.id, course_id=course_map["PHIL 10100"].id, status=StatusEnum.in_progress, semester="Fall 2023", credits_applied=3),
        StudentCourse(user_id=bob.id, course_id=course_map["COMM 10100"].id, status=StatusEnum.in_progress, semester="Fall 2023", credits_applied=3),
        StudentCourse(user_id=bob.id, course_id=course_map["PSYC 10100"].id, status=StatusEnum.planned),
        StudentCourse(user_id=bob.id, course_id=course_map["ECON 10100"].id, status=StatusEnum.planned),
    ]

    db.add_all(enrollments)
    db.commit()
    db.close()

    print("✅ Seed complete.")
    print(f"   {len(courses)} courses")
    print(f"   {len(requirements)} degree requirements")
    print(f"   {len(users)} users")
    print(f"   {len(enrollments)} enrollments")
    print(f"   Admin login: admin@admin.com / admin")


if __name__ == "__main__":
    seed()