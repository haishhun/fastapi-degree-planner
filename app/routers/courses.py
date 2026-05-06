from fastapi import Depends, HTTPException, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.routers.auth import get_current_user
from app.models import (
    Course,
    User,
    StudentCourse,
    StatusEnum,
)
from app.schemas import (
    StudentCoursePublic,
    StudentCourseCreate,
    StudentCourseUpdate,
    ResponseMessage,
)
from app.database import get_session

router = APIRouter()


@router.get("", response_model=list[StudentCoursePublic])
def list_courses(
    user: User = Depends(get_current_user), session: Session = Depends(get_session)
) -> list[StudentCoursePublic]:
    user_courses = (
        session.execute(select(StudentCourse).where(StudentCourse.user_id == user.id))
        .scalars()
        .all()
    )
    return user_courses


@router.get("/{id}", response_model=StudentCoursePublic)
def get_course(
    id: int,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> StudentCoursePublic:
    user_course = (
        session.execute(
            select(StudentCourse)
            .where(StudentCourse.user_id == user.id)
            .where(StudentCourse.id == id)
        )
        .scalars()
        .one_or_none()
    )
    if not user_course:
        raise HTTPException(status_code=404, detail=f"Course with {id} not found")
    return user_course


@router.post("", response_model=StudentCoursePublic)
def create_course(
    data: StudentCourseCreate,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> StudentCourse:
    course = (
        session.execute(select(Course).where(Course.code == data.code))
        .scalars()
        .one_or_none()
    )
    if not course:
        raise HTTPException(status_code=404, detail=f"Course {data.code} not found")

    if data.status in [StatusEnum.completed, StatusEnum.in_progress]:
        credits_applied = course.credits
    else:
        credits_applied = 0
    new_course = StudentCourse(
        user_id=user.id,
        course_id=course.id,
        semester=data.semester,
        status=data.status,
        grade=data.grade,
        grade_points=data.grade_points,
        credits_applied=credits_applied,
    )
    session.add(new_course)
    session.commit()
    session.refresh(new_course)
    return new_course


@router.patch("/{id}", response_model=StudentCoursePublic)
def update_course(
    id: int,
    data: StudentCourseUpdate,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> StudentCourse:

    user_course = (
        session.execute(
            select(StudentCourse)
            .where(StudentCourse.id == id)
            .where(StudentCourse.user_id == user.id)
        )
        .scalars()
        .one_or_none()
    )

    if not user_course:
        raise HTTPException(status_code=404, detail="Course not found")

    catalog_course = (
        session.execute(select(Course).where(Course.id == user_course.course_id))
        .scalars()
        .one_or_none()
    )
    if not catalog_course:
        raise HTTPException(status_code=404, detail="Course not found")

    update_data = data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(user_course, field, value)
    if user_course.status in [StatusEnum.completed, StatusEnum.in_progress]:
        user_course.credits_applied = catalog_course.credits
    else:
        user_course.credits_applied = 0
    session.commit()
    session.refresh(user_course)

    return user_course


@router.delete("/{id}", response_model=ResponseMessage)
def delete_course(
    id: int,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> ResponseMessage:

    course = (
        session.execute(
            select(StudentCourse)
            .where(StudentCourse.id == id)
            .where(StudentCourse.user_id == user.id)
        )
        .scalars()
        .one_or_none()
    )
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    session.delete(course)
    session.commit()

    return ResponseMessage(detail="Course has been deleted successfully.")
