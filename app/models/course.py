import enum

from sqlalchemy import Column, Integer, String, Enum, Boolean
from sqlalchemy.orm import relationship
from app.database import Base


class CategoryEnum(enum.Enum):
    core = "core"
    focus_study = "focus_study"
    elective = "elective"
    general = "general"


class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True)
    code = Column(String, nullable=False, unique=True)
    name = Column(String, nullable=False)
    credits = Column(Integer, nullable=False)
    category = Column(Enum(CategoryEnum), nullable=False)
    is_cs_elective_eligible = Column(Boolean, nullable=False, default=False)
    prereq_description = Column(String, nullable=True)
    min_grade_required = Column(String, nullable=True)

    students = relationship("StudentCourse", back_populates="course")
