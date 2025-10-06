from typing import Dict
from app.repositories.course_repository import CourseRepository
from app.repositories.lecture_repository import LectureRepository
from app.models.lab2_models import (
    CourseReportResponse,
    LectureWithStudentCountDto,
    Lecture
)


class ReportService:
    """Сервис для формирования отчетов по курсам и лекциям"""
    
    def __init__(
        self,
        course_repo: CourseRepository,
        lecture_repo: LectureRepository
    ) -> None:
        self._course_repo = course_repo
        self._lecture_repo = lecture_repo
    
    async def get_requirements(
        self, course_name: str, year: int
    ) -> CourseReportResponse:
        """
        Формирует отчет по курсу: получает курс, его лекции и количество студентов
        
        :param course_name: Название курса
        :param year: Год
        :return: Отчет с курсом и лекциями с количеством студентов
        """
        # Получаем курс из PostgreSQL
        course = self._course_repo.get_course_by_name(course_name)
        
        if not course:
            return CourseReportResponse(
                course=None,
                lectures=[]
            )
        
        # Получаем все лекции курса в указанном году из PostgreSQL
        lectures = self._lecture_repo.get_lectures_by_course_id(course.id, year)
        
        # Для каждой лекции получаем группы и количество студентов из Neo4j
        lecture_dict: Dict[int, int] = {}
        
        for lecture in lectures:
            groups = await self._lecture_repo.get_groups_with_student_count_for_lecture(
                lecture.id
            )
            
            # Суммируем студентов по всем группам
            total_students = sum(group.student_count for group in groups)
            lecture_dict[lecture.id] = total_students
        
        # Формируем DTO для ответа
        lectures_dto = [
            LectureWithStudentCountDto(
                lecture=lecture,
                student_count=lecture_dict.get(lecture.id, 0)
            )
            for lecture in lectures
        ]
        
        return CourseReportResponse(
            course=course,
            lectures=lectures_dto
        )
