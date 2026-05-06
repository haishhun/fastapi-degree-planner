import enum
from sqlalchemy import (
    Column,
    Integer,
    String,
    Enum,
    ForeignKey,
    Float,
)
from sqlalchemy.orm import relationship
from app.database import Base


class StatusEnum(enum.Enum):
    planned = "planned"
    in_progress = "in_progress"
    completed = "completed"


class StudentCourse(Base):
    __tablename__ = "student_courses"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    semester = Column(String, nullable=True)
    status = Column(Enum(StatusEnum), nullable=False)
    grade = Column(String, nullable=True)
    grade_points = Column(Float, nullable=True)
    credits_applied = Column(Float, nullable=True)
    user = relationship("User", back_populates="courses")

    course = relationship("Course", back_populates="students")
