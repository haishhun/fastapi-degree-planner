from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.database import get_session
from app.models import User, StudentCourse, StatusEnum, DegreeRequirement
from app.routers.auth import get_current_user
from app.schemas.stats import StatsPublic

router = APIRouter()


@router.get("/", response_model=StatsPublic)
def get_stats(
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> StatsPublic:
    completed_classes = (
        session.execute(
            select(StudentCourse)
            .options(joinedload(StudentCourse.course))
            .where(StudentCourse.user_id == user.id)
            .where(StudentCourse.status == StatusEnum.completed)
        )
        .scalars()
        .all()
    )
    in_progress_classes = (
        session.execute(
            select(StudentCourse)
            .options(joinedload(StudentCourse.course))
            .where(StudentCourse.user_id == user.id)
            .where(StudentCourse.status == StatusEnum.in_progress)
        )
        .scalars()
        .all()
    )
    degree_requirement = (
        session.execute(
            select(DegreeRequirement).where(DegreeRequirement.name == user.major)
        )
        .scalars()
        .one_or_none()
    )
    if degree_requirement is None:
        credits_required = 120
    else:
        credits_required = degree_requirement.credits_required

    cs_credits_applied = 0
    cs_completed_credits = 0
    cs_grade = 0
    cs_classes_completed = 0
    credits_applied = 0
    total_grade = 0
    completed_credits = 0

    for course in completed_classes:
        credits_applied += course.credits_applied
        completed_credits += course.credits_applied
        total_grade += course.grade_points * course.credits_applied
        if "CSCI" in course.course.code:
            cs_credits_applied += course.credits_applied
            cs_completed_credits += course.credits_applied
            cs_grade += course.grade_points * course.credits_applied
            cs_classes_completed += 1

    for course in in_progress_classes:
        credits_applied += course.credits_applied
        if "CSCI" in course.course.code:
            cs_credits_applied += course.credits_applied

    degree_progress_pct = (credits_applied * 100) / credits_required
    credits_remaining = credits_required - credits_applied
    gpa_cumulative = total_grade / completed_credits if completed_credits else 0
    gpa_cs_only = cs_grade / cs_completed_credits if cs_completed_credits else 0

    est_graduation = "Spring 2028"  # placeholder
    cs_credits_required = 45  # placeholder
    cs_credits_remaining = cs_credits_required - cs_credits_applied
    liberal_arts_credits = credits_applied - cs_credits_applied

    stats = StatsPublic(
        credits_required=credits_required,
        credits_applied=credits_applied,
        degree_progress_pct=degree_progress_pct,
        credits_remaining=credits_remaining,
        cs_credits_done=cs_credits_applied,
        cs_credits_required=cs_credits_required,
        cs_credits_remaining=cs_credits_remaining,
        gpa_cumulative=gpa_cumulative,
        gpa_cs_only=gpa_cs_only,
        est_graduation=est_graduation,
        liberal_arts_credits=liberal_arts_credits,
    )
    return stats
