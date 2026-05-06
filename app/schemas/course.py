from pydantic import BaseModel

from app.models import StatusEnum


class StudentCoursePublic(BaseModel):
    id: int
    user_id: int
    course_id: int
    semester: str | None = None
    status: StatusEnum
    grade: str | None = None
    grade_points: float | None = None
    credits_applied: float | None = None
    model_config = {"from_attributes": True}


class StudentCourseCreate(BaseModel):
    code: str
    semester: str | None = None
    status: StatusEnum
    grade: str | None = None
    grade_points: float | None = None


class StudentCourseUpdate(BaseModel):
    grade: str | None = None
    grade_points: float | None = None
    status: StatusEnum | None = None
    semester: str | None = None
