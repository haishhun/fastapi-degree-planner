from fastapi.testclient import TestClient


def test_list_courses_empty(client: TestClient):
    res = client.get("/api/v1/catalog/courses")
    assert res.status_code == 200
    assert res.json() == []


def test_list_courses_returns_all(client: TestClient, seed_courses):
    res = client.get("/api/v1/catalog/courses")
    assert res.status_code == 200
    assert len(res.json()) == 2


def test_list_courses_pagination(client: TestClient, seed_courses):
    res = client.get("/api/v1/catalog/courses?offset=0&limit=1")
    assert res.status_code == 200
    assert len(res.json()) == 1
    assert res.json()[0]["code"] == "CSCI 10100"


def test_list_courses_limit_too_high(client: TestClient):
    res = client.get("/api/v1/catalog/courses?limit=999")
    assert res.status_code == 422


def test_get_course_by_code_success(client: TestClient, seed_courses):
    res = client.get("/api/v1/catalog/courses/CSCI 12700")
    assert res.status_code == 200
    assert res.json()["code"] == "CSCI 12700"


def test_get_course_by_code_not_found(client: TestClient):
    res = client.get("/api/v1/catalog/courses/FAKE 00000")
    assert res.status_code == 404


def test_prereqs_success(client: TestClient, seed_courses):
    res = client.get("/api/v1/catalog/prereqs/check?code=CSCI 12700")
    assert res.status_code == 200
    data = res.json()
    assert data["code"] == "CSCI 12700"
    assert data["min_grade_required"] == "C"


def test_prereqs_null_fields(client: TestClient, seed_courses):
    res = client.get("/api/v1/catalog/prereqs/check?code=CSCI 10100")
    assert res.status_code == 200
    assert res.json()["prereq_description"] is None
    assert res.json()["min_grade_required"] is None


def test_prereqs_not_found(client: TestClient):
    res = client.get("/api/v1/catalog/prereqs/check?code=FAKE 00000")
    assert res.status_code == 404


def test_prereqs_missing_code(client: TestClient):
    res = client.get("/api/v1/catalog/prereqs/check")
    assert res.status_code == 422
