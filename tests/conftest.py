import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.models import CategoryEnum, Course, StudentCourse, StatusEnum
from app.database import get_session, Base

os.environ.setdefault("SECRET_KEY", "test-secret-key")

TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def override_get_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_session] = override_get_session


@pytest.fixture(autouse=True)
def reset_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture()
def db():
    database = TestingSessionLocal()
    try:
        yield database
    finally:
        database.close()


@pytest.fixture()
def seed_courses(db):
    courses = [
        Course(
            code="CSCI 10100",
            name="Introduction to Computing",
            credits=3,
            category=CategoryEnum.core,
            is_cs_elective_eligible=False,
        ),
        Course(
            code="CSCI 12700",
            name="Introduction to Computer Science",
            credits=3,
            category=CategoryEnum.core,
            is_cs_elective_eligible=True,
            prereq_description="High school math",
            min_grade_required="C",
        ),
    ]

    db.add_all(courses)
    db.commit()

    return courses


@pytest.fixture()
def registered_user(client: TestClient) -> dict:
    res = client.post(
        "/api/v1/auth/register",
        json={
            "name": "John Doe",
            "email": "john@example.com",
            "password": "secret123",
        },
    )

    return res.json()


@pytest.fixture()
def token(client: TestClient, registered_user: dict) -> str:
    res = client.post(
        "/api/v1/auth/login",
        data={
            "username": "john@example.com",
            "password": "secret123",
        },
    )

    return res.json()["access_token"]


@pytest.fixture()
def auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def enrolled_courses(db, registered_user, seed_courses):
    user_id = registered_user["id"]

    enrollments = [
        StudentCourse(
            user_id=user_id,
            course_id=course.id,
            status=StatusEnum.planned,
        )
        for course in seed_courses
    ]

    db.add_all(enrollments)
    db.commit()

    return enrollments
