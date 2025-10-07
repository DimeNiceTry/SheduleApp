from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import date as Date


# ===== Базовые модели из БД =====

class Student(BaseModel):
    """Модель студента из Redis"""
    model_config = ConfigDict(populate_by_name=True)
    
    id: int = Field(..., alias="Id")
    full_name: str = Field(..., alias="FullName")
    group_id: int = Field(..., alias="GroupId")
    date_of_recipient: Date = Field(..., alias="DateOfRecipient")


class Group(BaseModel):
    """Модель группы из MongoDB"""
    model_config = ConfigDict(populate_by_name=True)
    
    id: int = Field(..., alias="Id")
    name: str = Field(..., alias="Name")
    department_id: int = Field(..., alias="DepartmentId")
    year: int = Field(..., alias="Year")


class Course(BaseModel):
    """Модель курса из PostgreSQL"""
    model_config = ConfigDict(populate_by_name=True)
    
    id: int = Field(..., alias="Id")
    name: str = Field(..., alias="Name")
    department_id: int = Field(..., alias="DepartmentId")
    speciality_id: int = Field(..., alias="SpecialityId")
    term: str = Field(..., alias="Term")


class Lecture(BaseModel):
    """Модель лекции из PostgreSQL"""
    model_config = ConfigDict(populate_by_name=True)
    
    id: int = Field(..., alias="Id")
    name: str = Field(..., alias="Name")
    requirements: bool = Field(..., alias="Requirements")
    year: int = Field(..., alias="Year")
    course_id: int = Field(..., alias="CourseId")


class Schedule(BaseModel):
    """Модель расписания из PostgreSQL"""
    model_config = ConfigDict(populate_by_name=True)
    
    id: int = Field(..., alias="Id")
    lecture_id: int = Field(..., alias="LectureId")
    group_id: int = Field(..., alias="GroupId")
    date: Date = Field(..., alias="Date")


class Visit(BaseModel):
    """Модель посещения из PostgreSQL"""
    model_config = ConfigDict(populate_by_name=True)
    
    id: int = Field(..., alias="Id")
    student_id: int = Field(..., alias="StudentId")
    schedule_id: int = Field(..., alias="ScheduleId")


# ===== DTO для отчета =====

class StudentDTO(BaseModel):
    """DTO студента с информацией о часах"""
    student: Student
    all_hours: int = Field(..., description="Всего запланированных часов")
    visit_hours: int = Field(..., description="Посещенных часов")


class GroupDTO(BaseModel):
    """DTO группы со списком студентов"""
    group: Group
    students: List[StudentDTO]


class CourseDTO(BaseModel):
    """DTO с информацией о курсах и лекциях"""
    courses: List[Course]
    lectures: List[Lecture]


class GroupReportResponse(BaseModel):
    """Ответ с отчетом по группе"""
    model_config = ConfigDict(populate_by_name=True)
    
    course_info: Optional[CourseDTO] = Field(None, alias="CourseInfo")
    group_info: Optional[GroupDTO] = Field(None, alias="GroupInfo")
    message: Optional[str] = Field(None, alias="Message")
