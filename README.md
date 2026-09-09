# CS Degree Planner

Full-stack degree planning application for Hunter College Computer Science students.

Built with:

* FastAPI
* SQLAlchemy 2.0
* JWT Authentication
* Pytest
* SQLite / PostgreSQL
* React (planned)

---

## Overview

CS Degree Planner is a full-stack web application designed to help students track their degree progress, manage semester planning, monitor GPA, and validate course prerequisites.

The project began as a static HTML degree tracker and is being transformed into a fully data-driven application with:

* User authentication
* Persistent database storage
* Automatic degree progress calculations
* GPA tracking
* Requirement fulfillment tracking
* Prerequisite validation
* Interactive dashboard frontend

---

## Features

### Authentication

* JWT-based authentication
* User registration and login
* Protected API routes
* Password hashing with bcrypt

### Course Planning

* Add courses to degree plan
* Update course status and grades
* Delete planned courses
* Semester organization

### Catalog System

* Read-only course catalog
* Degree requirements catalog
* Prerequisite reference system

### Degree Tracking

* Credits applied
* Credits remaining
* Degree progress percentage
* GPA calculations (planned)
* Requirement fulfillment tracking (planned)

### Backend Quality

* Modular FastAPI architecture
* SQLAlchemy ORM relationships
* Integration tests with pytest
* API versioning (`/api/v1`)
* OpenAPI / Swagger documentation

---

## Tech Stack

### Backend

* FastAPI
* SQLAlchemy 2.0
* Pydantic v2
* SQLite
* PostgreSQL (planned)
* JWT (`python-jose`)
* bcrypt
* Pytest

### Frontend (planned)

* React + Vite
* Fetch API
* Dark dashboard UI

---

## API Endpoints

### Auth

| Method | Endpoint                |
| ------ | ----------------------- |
| POST   | `/api/v1/auth/register` |
| POST   | `/api/v1/auth/login`    |
| GET    | `/api/v1/auth/me`       |

### Courses

| Method | Endpoint               |
| ------ | ---------------------- |
| GET    | `/api/v1/courses`      |
| POST   | `/api/v1/courses`      |
| PATCH  | `/api/v1/courses/{id}` |
| DELETE | `/api/v1/courses/{id}` |

### Catalog

| Method | Endpoint                         |
| ------ | -------------------------------- |
| GET    | `/api/v1/catalog/courses`        |
| GET    | `/api/v1/catalog/courses/{code}` |
| GET    | `/api/v1/catalog/requirements`   |
| GET    | `/api/v1/catalog/prereqs/check`  |

### Stats

| Method | Endpoint        |
| ------ | --------------- |
| GET    | `/api/v1/stats` |

---

## Running the Project

### 1. Clone repository

```bash
git clone https://github.com/YOUR_USERNAME/fastapi-degree-planner.git
cd fastapi-degree-planner
```

### 2. Create virtual environment

```bash
python -m venv venv
```

### 3. Activate virtual environment

#### macOS / Linux

```bash
source venv/bin/activate
```

#### Windows

```bash
venv\Scripts\activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Create `.env`

```env
SECRET_KEY=your_secret_key_here
```

### 6. Run server

```bash
uvicorn app.main:app --reload
```

---

## API Documentation

Swagger UI:

```txt
http://localhost:8000/docs
```

ReDoc:

```txt
http://localhost:8000/redoc
```

---

## Testing

Run integration tests:

```bash
pytest
```

The backend includes tests for:

* Authentication
* Authorization
* CRUD operations
* PATCH semantics
* Catalog endpoints
* Validation behavior

---

## Author

Dzmitry Haishun

Hunter College Computer Science Student
