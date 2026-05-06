from app.models import StudentCourse, StatusEnum


class TestListCourses:
    def test_returns_all_user_courses(self, client, auth_headers, enrolled_courses):
        response = client.get("/api/v1/courses/", headers=auth_headers)

        assert response.status_code == 200
        assert len(response.json()) == len(enrolled_courses)

    def test_returns_empty_list_when_no_courses(self, client, auth_headers):
        response = client.get("/api/v1/courses/", headers=auth_headers)

        assert response.status_code == 200
        assert response.json() == []

    def test_requires_authentication(self, client):
        response = client.get("/api/v1/courses/")

        assert response.status_code == 401


class TestGetCourse:
    def test_returns_course_when_found(self, client, auth_headers, enrolled_courses):
        course_id = enrolled_courses[0].id

        response = client.get(f"/api/v1/courses/{course_id}", headers=auth_headers)

        assert response.status_code == 200
        assert response.json()["id"] == course_id

    def test_returns_404_when_course_does_not_exist(self, client, auth_headers):
        response = client.get("/api/v1/courses/999", headers=auth_headers)

        assert response.status_code == 404
        assert "999" in response.json()["detail"]

    def test_cannot_access_another_users_course(
        self, client, db, seed_courses, enrolled_courses
    ):
        other = client.post(
            "/api/v1/auth/register",
            json={"name": "Jane", "email": "jane@example.com", "password": "secret123"},
        ).json()
        other_enrollment = StudentCourse(
            user_id=other["id"], course_id=seed_courses[0].id, status=StatusEnum.planned
        )
        db.add(other_enrollment)
        db.commit()

        token = client.post(
            "/api/v1/auth/login",
            data={"username": "john@example.com", "password": "secret123"},
        ).json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        response = client.get(f"/api/v1/courses/{other_enrollment.id}", headers=headers)

        assert response.status_code == 404

    def test_requires_authentication(self, client, enrolled_courses):
        course_id = enrolled_courses[0].id

        response = client.get(f"/api/v1/courses/{course_id}")

        assert response.status_code == 401


class TestCreateCourse:
    def test_creates_course_successfully(self, client, auth_headers, seed_courses):
        response = client.post(
            "/api/v1/courses/",
            json={"code": "CSCI 10100", "status": "planned"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "planned"
        assert data["credits_applied"] == 0

    def test_credits_applied_when_completed(self, client, auth_headers, seed_courses):
        response = client.post(
            "/api/v1/courses/",
            json={
                "code": "CSCI 10100",
                "status": "completed",
                "grade": "A",
                "grade_points": 4.0,
            },
            headers=auth_headers,
        )

        assert response.status_code == 200
        assert response.json()["credits_applied"] == 3

    def test_credits_applied_when_in_progress(self, client, auth_headers, seed_courses):
        response = client.post(
            "/api/v1/courses/",
            json={"code": "CSCI 10100", "status": "in_progress"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        assert response.json()["credits_applied"] == 3

    def test_returns_404_for_unknown_course_code(self, client, auth_headers):
        response = client.post(
            "/api/v1/courses/",
            json={"code": "FAKE 00000", "status": "planned"},
            headers=auth_headers,
        )

        assert response.status_code == 404
        assert "FAKE 00000" in response.json()["detail"]

    def test_requires_authentication(self, client, seed_courses):
        response = client.post(
            "/api/v1/courses/",
            json={"code": "CSCI 10100", "status": "planned"},
        )

        assert response.status_code == 401

    def test_stores_semester_when_provided(self, client, auth_headers, seed_courses):
        response = client.post(
            "/api/v1/courses/",
            json={"code": "CSCI 10100", "status": "planned", "semester": "Fall 2025"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        assert response.json()["semester"] == "Fall 2025"


class TestUpdateCourse:
    def test_updates_status_successfully(self, client, auth_headers, enrolled_courses):
        course_id = enrolled_courses[0].id

        response = client.patch(
            f"/api/v1/courses/{course_id}",
            json={"status": "in_progress"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        assert response.json()["status"] == "in_progress"

    def test_credits_applied_updates_when_status_changes_to_completed(
        self, client, auth_headers, enrolled_courses
    ):
        course_id = enrolled_courses[0].id

        response = client.patch(
            f"/api/v1/courses/{course_id}",
            json={"status": "completed"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        assert response.json()["credits_applied"] == 3

    def test_credits_cleared_when_status_changes_to_planned(
        self, client, auth_headers, db, registered_user, seed_courses
    ):
        enrollment = StudentCourse(
            user_id=registered_user["id"],
            course_id=seed_courses[0].id,
            status=StatusEnum.completed,
            credits_applied=3,
        )
        db.add(enrollment)
        db.commit()

        response = client.patch(
            f"/api/v1/courses/{enrollment.id}",
            json={"status": "planned"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        assert response.json()["credits_applied"] == 0

    def test_updates_grade_and_grade_points(
        self, client, auth_headers, enrolled_courses
    ):
        course_id = enrolled_courses[0].id

        response = client.patch(
            f"/api/v1/courses/{course_id}",
            json={"grade": "B+", "grade_points": 3.3},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["grade"] == "B+"
        assert data["grade_points"] == 3.3

    def test_returns_404_when_course_not_found(self, client, auth_headers):
        response = client.patch(
            "/api/v1/courses/999",
            json={"status": "completed"},
            headers=auth_headers,
        )

        assert response.status_code == 404

    def test_cannot_update_another_users_course(
        self, client, db, seed_courses, enrolled_courses
    ):
        other = client.post(
            "/api/v1/auth/register",
            json={"name": "Jane", "email": "jane@example.com", "password": "secret123"},
        ).json()
        other_enrollment = StudentCourse(
            user_id=other["id"],
            course_id=seed_courses[0].id,
            status=StatusEnum.planned,
        )
        db.add(other_enrollment)
        db.commit()

        token = client.post(
            "/api/v1/auth/login",
            data={"username": "john@example.com", "password": "secret123"},
        ).json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        response = client.patch(
            f"/api/v1/courses/{other_enrollment.id}",
            json={"status": "completed"},
            headers=headers,
        )

        assert response.status_code == 404

    def test_requires_authentication(self, client, enrolled_courses):
        course_id = enrolled_courses[0].id

        response = client.patch(
            f"/api/v1/courses/{course_id}", json={"status": "completed"}
        )

        assert response.status_code == 401

    def test_partial_update_does_not_overwrite_unset_fields(
        self, client, auth_headers, db, registered_user, seed_courses
    ):
        enrollment = StudentCourse(
            user_id=registered_user["id"],
            course_id=seed_courses[0].id,
            status=StatusEnum.planned,
            semester="Spring 2025",
        )
        db.add(enrollment)
        db.commit()

        response = client.patch(
            f"/api/v1/courses/{enrollment.id}",
            json={"grade": "A"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["semester"] == "Spring 2025"
        assert data["grade"] == "A"


class TestDeleteCourse:
    def test_deletes_course_successfully(self, client, auth_headers, enrolled_courses):
        course_id = enrolled_courses[0].id

        response = client.delete(f"/api/v1/courses/{course_id}", headers=auth_headers)

        assert response.status_code == 200
        assert response.json()["detail"] == "Course has been deleted successfully."

    def test_course_no_longer_accessible_after_deletion(
        self, client, auth_headers, enrolled_courses
    ):
        course_id = enrolled_courses[0].id
        client.delete(f"/api/v1/courses/{course_id}", headers=auth_headers)

        response = client.get(f"/api/v1/courses/{course_id}", headers=auth_headers)

        assert response.status_code == 404

    def test_returns_404_when_course_not_found(self, client, auth_headers):
        response = client.delete("/api/v1/courses/999", headers=auth_headers)

        assert response.status_code == 404

    def test_cannot_delete_another_users_course(
        self, client, db, seed_courses, enrolled_courses
    ):
        other = client.post(
            "/api/v1/auth/register",
            json={"name": "Jane", "email": "jane@example.com", "password": "secret123"},
        ).json()
        other_enrollment = StudentCourse(
            user_id=other["id"],
            course_id=seed_courses[0].id,
            status=StatusEnum.planned,
        )
        db.add(other_enrollment)
        db.commit()

        token = client.post(
            "/api/v1/auth/login",
            data={"username": "john@example.com", "password": "secret123"},
        ).json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        response = client.delete(
            f"/api/v1/courses/{other_enrollment.id}", headers=headers
        )

        assert response.status_code == 404

    def test_requires_authentication(self, client, enrolled_courses):
        course_id = enrolled_courses[0].id

        response = client.delete(f"/api/v1/courses/{course_id}")

        assert response.status_code == 401
