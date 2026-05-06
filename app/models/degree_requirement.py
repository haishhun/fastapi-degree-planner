from sqlalchemy import Column, Integer, String, Enum

from app.database import Base
from app.models.course import CategoryEnum


class DegreeRequirement(Base):
    __tablename__ = "degree_requirements"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    credits_required = Column(Integer, nullable=False)
    category_filter = Column(Enum(CategoryEnum), nullable=False)
    notes = Column(String, nullable=True)
