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


class EstGraduationEnum(enum.Enum):
    spring_26 = "Spring 2026"
    summer_26 = "Summer 2026"
    fall_26 = "Fall 2026"
    spring_27 = "Spring 2027"
    summer_27 = "Summer 2027"
    fall_27 = "Fall 2027"
    spring_28 = "Spring 2028"
    summer_28 = "Summer 2028"
    fall_28 = "Fall 2028"
    spring_29 = "Spring 2029"
    summer_29 = "Summer 2029"
    fall_29 = "Fall 2029"
    spring_30 = "Spring 2030"
    summer_30 = "Summer 2030"
    fall_30 = "Fall 2030"
