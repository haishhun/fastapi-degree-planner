from pydantic import BaseModel, ConfigDict

from app.models import CategoryEnum


class CoursePublic(BaseModel):
    id: int
    code: str
    name: str
    credits: int
    category: CategoryEnum
    is_cs_elective_eligible: bool
    prereq_description: str | None = None
    min_grade_required: str | None = None

    model_config = ConfigDict(from_attributes=True)


class CoursePrereqPublic(BaseModel):
    code: str
    prereq_description: str | None = None
    min_grade_required: str | None = None

    model_config = ConfigDict(from_attributes=True)


class DegreeRequirementPublic(BaseModel):
    id: int
    name: str
    credits_required: int
    category_filter: CategoryEnum
    notes: str | None = None

    model_config = ConfigDict(from_attributes=True)
