import pytest
from app.models import DegreeRequirement, StudentCourse, StatusEnum, CategoryEnum, Course


@pytest.fixture()
def seed_degree_requirement(db):
    req = DegreeRequirement(
        name="Computer Science",
        credits_required=120,
        category_filter=CategoryEnum.core,
    )
    db.add(req)
    db.commit()
    return req


@pytest.fixture()
def registered_user_cs(client, db):
    res = client.post(
        "/api/v1/auth/register",
        json={
            "name": "Jane Doe",
            "email": "jane@example.com",
            "password": "secret123",
            "major": "Computer Science",
        },
    )
    return res.json()


@pytest.fixture()
def token_cs(client, registered_user_cs):
    res = client.post(
        "/api/v1/auth/login",
        data={"username": "jane@example.com", "password": "secret123"},
    )
    return res.json()["access_token"]


@pytest.fixture()
def auth_headers_cs(token_cs):
    return {"Authorization": f"Bearer {token_cs}"}


@pytest.fixture()
def seed_all_courses(db):
    courses = [
        Course(code="CSCI 10100", name="Intro to Computing", credits=3, category=CategoryEnum.core, is_cs_elective_eligible=False),        # 0
        Course(code="CSCI 12700", name="Intro to CS", credits=3, category=CategoryEnum.core, is_cs_elective_eligible=True),                # 1
        Course(code="CSCI 21000", name="Data Structures", credits=3, category=CategoryEnum.core, is_cs_elective_eligible=True),            # 2
        Course(code="CSCI 31500", name="Software Engineering", credits=3, category=CategoryEnum.focus_study, is_cs_elective_eligible=True), # 3
        Course(code="CSCI 40100", name="Machine Learning", credits=3, category=CategoryEnum.elective, is_cs_elective_eligible=True),       # 4
        Course(code="ENGL 10100", name="English Composition", credits=3, category=CategoryEnum.general, is_cs_elective_eligible=False),    # 5
        Course(code="ENGL 21000", name="Technical Writing", credits=3, category=CategoryEnum.general, is_cs_elective_eligible=False),      # 6
        Course(code="MATH 20100", name="Calculus I", credits=4, category=CategoryEnum.general, is_cs_elective_eligible=False),             # 7
        Course(code="MATH 20200", name="Calculus II", credits=4, category=CategoryEnum.general, is_cs_elective_eligible=False),            # 8
        Course(code="PHIL 10100", name="Ethics in Technology", credits=3, category=CategoryEnum.general, is_cs_elective_eligible=False),   # 9
    ]
    db.add_all(courses)
    db.commit()
    return courses


def enroll(db, user_id, course, status, grade_points=0.0, credits_applied=None):
    sc = StudentCourse(
        user_id=user_id,
        course_id=course.id,
        status=status,
        grade_points=grade_points,
        credits_applied=credits_applied or course.credits,
    )
    db.add(sc)
    db.commit()
    return sc


# ── Basic response shape ──────────────────────────────────────────────────────

def test_stats_returns_200(client, auth_headers, seed_degree_requirement, registered_user):
    res = client.get("/api/v1/stats/", headers=auth_headers)
    assert res.status_code == 200


def test_stats_response_has_required_fields(client, auth_headers, seed_degree_requirement):
    res = client.get("/api/v1/stats/", headers=auth_headers)
    data = res.json()
    expected_keys = [
        "credits_applied", "credits_required", "degree_progress_pct",
        "credits_remaining", "cs_credits_done", "cs_credits_required",
        "cs_credits_remaining", "gpa_cumulative", "gpa_cs_only",
        "est_graduation", "liberal_arts_credits",
    ]
    for key in expected_keys:
        assert key in data, f"Missing key: {key}"


def test_stats_unauthenticated_returns_401(client):
    res = client.get("/api/v1/stats/")
    assert res.status_code == 401


# ── Zero courses ──────────────────────────────────────────────────────────────

def test_stats_no_courses_zeros(client, auth_headers, seed_degree_requirement):
    res = client.get("/api/v1/stats/", headers=auth_headers)
    data = res.json()
    assert data["credits_applied"] == 0
    assert data["gpa_cumulative"] == 0
    assert data["gpa_cs_only"] == 0
    assert data["cs_credits_done"] == 0
    assert data["liberal_arts_credits"] == 0


def test_stats_no_courses_full_credits_remaining(client, auth_headers, seed_degree_requirement):
    res = client.get("/api/v1/stats/", headers=auth_headers)
    data = res.json()
    assert data["credits_remaining"] == data["credits_required"]
    assert data["degree_progress_pct"] == 0


# ── credits_applied ───────────────────────────────────────────────────────────

def test_stats_completed_credits_counted(client, auth_headers_cs, registered_user_cs, seed_all_courses, seed_degree_requirement, db):
    csci = seed_all_courses[0]
    engl = seed_all_courses[5]
    enroll(db, registered_user_cs["id"], csci, StatusEnum.completed, grade_points=4.0)
    enroll(db, registered_user_cs["id"], engl, StatusEnum.completed, grade_points=3.0)

    res = client.get("/api/v1/stats/", headers=auth_headers_cs)
    data = res.json()
    assert data["credits_applied"] == 6


def test_stats_in_progress_credits_counted(client, auth_headers_cs, registered_user_cs, seed_all_courses, seed_degree_requirement, db):
    csci2 = seed_all_courses[1]
    math = seed_all_courses[7]
    enroll(db, registered_user_cs["id"], csci2, StatusEnum.in_progress)
    enroll(db, registered_user_cs["id"], math, StatusEnum.in_progress)

    res = client.get("/api/v1/stats/", headers=auth_headers_cs)
    data = res.json()
    assert data["credits_applied"] == 7


def test_stats_planned_courses_not_counted(client, auth_headers_cs, registered_user_cs, seed_all_courses, seed_degree_requirement, db):
    csci = seed_all_courses[0]
    enroll(db, registered_user_cs["id"], csci, StatusEnum.planned)

    res = client.get("/api/v1/stats/", headers=auth_headers_cs)
    data = res.json()
    assert data["credits_applied"] == 0


# ── GPA ───────────────────────────────────────────────────────────────────────

def test_stats_gpa_cumulative_correct(client, auth_headers_cs, registered_user_cs, seed_all_courses, seed_degree_requirement, db):
    csci = seed_all_courses[0]
    engl = seed_all_courses[5]
    # 4.0 * 3 credits + 3.0 * 3 credits = 21 / 6 credits = 3.5
    enroll(db, registered_user_cs["id"], csci, StatusEnum.completed, grade_points=4.0, credits_applied=3)
    enroll(db, registered_user_cs["id"], engl, StatusEnum.completed, grade_points=3.0, credits_applied=3)

    res = client.get("/api/v1/stats/", headers=auth_headers_cs)
    assert res.json()["gpa_cumulative"] == pytest.approx(3.5)


def test_stats_gpa_cs_only_correct(client, auth_headers_cs, registered_user_cs, seed_all_courses, seed_degree_requirement, db):
    csci = seed_all_courses[0]
    csci2 = seed_all_courses[1]
    engl = seed_all_courses[5]
    enroll(db, registered_user_cs["id"], csci, StatusEnum.completed, grade_points=4.0, credits_applied=3)
    enroll(db, registered_user_cs["id"], csci2, StatusEnum.completed, grade_points=3.0, credits_applied=3)
    enroll(db, registered_user_cs["id"], engl, StatusEnum.completed, grade_points=2.0, credits_applied=3)

    res = client.get("/api/v1/stats/", headers=auth_headers_cs)
    # (4.0*3 + 3.0*3) / 6 = 3.5, engl should not affect cs gpa
    assert res.json()["gpa_cs_only"] == pytest.approx(3.5)


def test_stats_in_progress_does_not_affect_gpa(client, auth_headers_cs, registered_user_cs, seed_all_courses, seed_degree_requirement, db):
    csci = seed_all_courses[0]
    csci2 = seed_all_courses[1]
    enroll(db, registered_user_cs["id"], csci, StatusEnum.completed, grade_points=4.0, credits_applied=3)
    enroll(db, registered_user_cs["id"], csci2, StatusEnum.in_progress, credits_applied=3)

    res = client.get("/api/v1/stats/", headers=auth_headers_cs)
    # only csci counts: 4.0*3 / 3 = 4.0
    assert res.json()["gpa_cumulative"] == pytest.approx(4.0)


def test_stats_gpa_zero_when_no_completed(client, auth_headers_cs, registered_user_cs, seed_all_courses, seed_degree_requirement, db):
    csci = seed_all_courses[0]
    enroll(db, registered_user_cs["id"], csci, StatusEnum.in_progress)

    res = client.get("/api/v1/stats/", headers=auth_headers_cs)
    assert res.json()["gpa_cumulative"] == 0
    assert res.json()["gpa_cs_only"] == 0


# ── CS credits ───────────────────────────────────────────────────────────────

def test_stats_cs_credits_only_counts_csci_courses(client, auth_headers_cs, registered_user_cs, seed_all_courses, seed_degree_requirement, db):
    csci = seed_all_courses[0]
    engl = seed_all_courses[5]
    math = seed_all_courses[7]
    enroll(db, registered_user_cs["id"], csci, StatusEnum.completed, grade_points=4.0)
    enroll(db, registered_user_cs["id"], engl, StatusEnum.completed, grade_points=3.0)
    enroll(db, registered_user_cs["id"], math, StatusEnum.completed, grade_points=3.7)

    res = client.get("/api/v1/stats/", headers=auth_headers_cs)
    assert res.json()["cs_credits_done"] == 3  # only csci counts


def test_stats_cs_credits_includes_in_progress(client, auth_headers_cs, registered_user_cs, seed_all_courses, seed_degree_requirement, db):
    csci = seed_all_courses[0]
    csci2 = seed_all_courses[1]
    enroll(db, registered_user_cs["id"], csci, StatusEnum.completed, grade_points=4.0)
    enroll(db, registered_user_cs["id"], csci2, StatusEnum.in_progress)

    res = client.get("/api/v1/stats/", headers=auth_headers_cs)
    assert res.json()["cs_credits_done"] == 6


# ── Degree progress ───────────────────────────────────────────────────────────

def test_stats_degree_progress_pct(client, auth_headers_cs, registered_user_cs, seed_all_courses, seed_degree_requirement, db):
    csci = seed_all_courses[0]
    engl = seed_all_courses[5]
    enroll(db, registered_user_cs["id"], csci, StatusEnum.completed, grade_points=4.0)
    enroll(db, registered_user_cs["id"], engl, StatusEnum.completed, grade_points=3.0)

    res = client.get("/api/v1/stats/", headers=auth_headers_cs)
    data = res.json()
    assert data["degree_progress_pct"] == pytest.approx(6 * 100 / 120)


def test_stats_credits_remaining(client, auth_headers_cs, registered_user_cs, seed_all_courses, seed_degree_requirement, db):
    csci = seed_all_courses[0]
    enroll(db, registered_user_cs["id"], csci, StatusEnum.completed, grade_points=4.0)

    res = client.get("/api/v1/stats/", headers=auth_headers_cs)
    data = res.json()
    assert data["credits_remaining"] == 120 - 3


# ── Liberal arts ──────────────────────────────────────────────────────────────

def test_stats_liberal_arts_credits(client, auth_headers_cs, registered_user_cs, seed_all_courses, seed_degree_requirement, db):
    csci = seed_all_courses[0]
    engl = seed_all_courses[5]
    math = seed_all_courses[7]
    enroll(db, registered_user_cs["id"], csci, StatusEnum.completed, grade_points=4.0)
    enroll(db, registered_user_cs["id"], engl, StatusEnum.completed, grade_points=3.0)
    enroll(db, registered_user_cs["id"], math, StatusEnum.completed, grade_points=3.7)

    res = client.get("/api/v1/stats/", headers=auth_headers_cs)
    # 3 (engl) + 4 (math) = 7 non-cs credits
    assert res.json()["liberal_arts_credits"] == 7


# ── No degree requirement fallback ────────────────────────────────────────────

def test_stats_no_degree_requirement_falls_back_to_120(client, auth_headers, registered_user):
    res = client.get("/api/v1/stats/", headers=auth_headers)
    assert res.status_code == 200
    assert res.json()["credits_required"] == 120