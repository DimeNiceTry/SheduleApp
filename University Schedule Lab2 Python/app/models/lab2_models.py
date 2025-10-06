from pydantic import BaseModel, Field
from typing import Optional


class Course(BaseModel):
    """Модель курса"""
    id: int = Field(..., alias="Id")
    name: str = Field(..., alias="Name")
    department_id: int = Field(..., alias="DepartmentId")
    speciality_id: int = Field(..., alias="SpecialityId")
    term: str = Field(..., alias="Term")

    class Config:
        populate_by_name = True


class Lecture(BaseModel):
    """Модель лекции"""
    id: int = Field(..., alias="Id")
    name: str = Field(..., alias="Name")
    requirements: bool = Field(..., alias="Requirements")
    year: int = Field(..., alias="Year")
    course_id: int = Field(..., alias="CourseId")

    class Config:
        populate_by_name = True


class GroupStudentCountDto(BaseModel):
    """DTO для группы с количеством студентов"""
    group_id: int
    student_count: int


class LectureWithStudentCountDto(BaseModel):
    """DTO для лекции с количеством студентов"""
    lecture: Lecture
    student_count: int


class CourseReportResponse(BaseModel):
    """Ответ с отчетом по курсу"""
    course: Course
    lectures: list[LectureWithStudentCountDto]
