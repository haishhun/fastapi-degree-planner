from fastapi import Depends, Query, HTTPException, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models import Course, DegreeRequirement
from app.database import get_session
from app.schemas import CoursePublic, DegreeRequirementPublic, CoursePrereqPublic

router = APIRouter()


@router.get("/courses", response_model=list[CoursePublic])
def list_catalog_courses(
    *,
    session: Session = Depends(get_session),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, le=100),
) -> list[CoursePublic]:
    courses = (
        session.execute(select(Course).offset(offset).limit(limit)).scalars().all()
    )
    return courses


@router.get("/courses/{code}", response_model=CoursePublic)
def get_catalog_course(
    code: str,
    session: Session = Depends(get_session),
) -> CoursePublic:
    course = (
        session.execute(select(Course).where(Course.code == code))
        .scalars()
        .one_or_none()
    )
    if not course:
        raise HTTPException(status_code=404, detail=f"Course {code} not found")
    return course


@router.get("/requirements", response_model=list[DegreeRequirementPublic])
def list_catalog_requirements(
    *,
    session: Session = Depends(get_session),
) -> list[DegreeRequirementPublic]:
    requirements = session.execute(select(DegreeRequirement)).scalars().all()
    return requirements


@router.get("/prereqs/check", response_model=CoursePrereqPublic)
def check_prerequisites(
    *,
    code: str = Query(..., description="Course code e.g. CSCI 12700"),
    session: Session = Depends(get_session),
) -> CoursePrereqPublic:
    course = (
        (session.execute(select(Course).where(Course.code == code)))
        .scalars()
        .one_or_none()
    )
    if not course:
        raise HTTPException(status_code=404, detail=f"Course {code} not found")
    return course
