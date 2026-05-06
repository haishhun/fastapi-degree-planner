from datetime import datetime, UTC, timedelta

import os
import pytest
from fastapi.testclient import TestClient
from jose import jwt


def test_register_success(client: TestClient):
    res = client.post(
        "/api/v1/auth/register",
        json={
            "name": "John Doe",
            "email": "john@example.com",
            "password": "secret123",
        },
    )
    assert res.status_code == 201
    data = res.json()
    assert data["email"] == "john@example.com"
    assert "hashed_password" not in data


def test_register_duplicate_email(client: TestClient):
    payload = {"name": "John", "email": "john@example.com", "password": "secret123"}
    client.post("/api/v1/auth/register", json=payload)
    res = client.post("/api/v1/auth/register", json=payload)
    assert res.status_code == 409


def test_register_invalid_email(client: TestClient):
    res = client.post(
        "/api/v1/auth/register",
        json={
            "name": "John",
            "email": "notanemail",
            "password": "secret123",
        },
    )
    assert res.status_code == 422


def test_login_success(client: TestClient, registered_user: dict):
    res = client.post(
        "/api/v1/auth/login",
        data={
            "username": "john@example.com",
            "password": "secret123",
        },
    )
    assert res.status_code == 200
    assert "access_token" in res.json()
    assert res.json()["token_type"] == "bearer"


def test_login_wrong_password(client: TestClient, registered_user: dict):
    res = client.post(
        "/api/v1/auth/login",
        data={
            "username": "john@example.com",
            "password": "wrongpassword",
        },
    )
    assert res.status_code == 401


def test_login_user_not_found(client: TestClient):
    res = client.post(
        "/api/v1/auth/login",
        data={
            "username": "nobody@example.com",
            "password": "secret123",
        },
    )
    assert res.status_code == 401


def test_me_success(client: TestClient, auth_headers: dict):
    res = client.get("/api/v1/auth/me", headers=auth_headers)
    assert res.status_code == 200
    assert res.json()["email"] == "john@example.com"


def test_me_no_token(client: TestClient):
    res = client.get("/api/v1/auth/me")
    assert res.status_code == 401


def test_me_invalid_token(client: TestClient):
    res = client.get(
        "/api/v1/auth/me", headers={"Authorization": "Bearer invalidtoken"}
    )
    assert res.status_code == 401


def test_me_expired_token(client: TestClient, registered_user: dict):
    payload = {
        "sub": str(registered_user["id"]),
        "exp": datetime.now(UTC) - timedelta(minutes=1),
    }
    expired_token = jwt.encode(payload, os.getenv("SECRET_KEY"), algorithm="HS256")
    res = client.get(
        "/api/v1/auth/me", headers={"Authorization": f"Bearer {expired_token}"}
    )
    assert res.status_code == 401


def test_me_token_missing_sub(client: TestClient):
    token = jwt.encode({"foo": "bar"}, os.getenv("SECRET_KEY"), algorithm="HS256")
    res = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 401
