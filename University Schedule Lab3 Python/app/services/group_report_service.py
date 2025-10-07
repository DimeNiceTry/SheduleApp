from typing import Optional, Dict, List
from ..models.lab3_models import (
    GroupReportResponse, 
    CourseDTO, 
    GroupDTO, 
    StudentDTO,
    Student
)
from ..repositories.group_repository import GroupRepository
from ..repositories.student_repository import StudentRepository
from ..repositories.course_repository import CourseRepository
from ..repositories.lecture_repository import LectureRepository
from ..repositories.schedule_repository import ScheduleRepository
from ..repositories.visits_repository import VisitsRepository


class GroupReportService:
    """Сервис для генерации отчета по группе"""
    
    def __init__(
        self,
        group_repo: GroupRepository,
        student_repo: StudentRepository,
        course_repo: CourseRepository,
        lecture_repo: LectureRepository,
        schedule_repo: ScheduleRepository,
        visits_repo: VisitsRepository
    ):
        self.group_repo = group_repo
        self.student_repo = student_repo
        self.course_repo = course_repo
        self.lecture_repo = lecture_repo
        self.schedule_repo = schedule_repo
        self.visits_repo = visits_repo
    
    async def get_group_report(self, group_name: str) -> GroupReportResponse:
        """
        Получить отчет по группе:
        1. Найти группу по имени
        2. Получить студентов и лекции из Neo4j
        3. Найти специальные курсы (по департаменту)
        4. Посчитать общие часы (кол-во занятий * 2)
        5. Посчитать посещенные часы для каждого студента
        """
        # 1. Найти группу
        group = await self.group_repo.get_by_name(group_name)
        if not group:
            return GroupReportResponse(
                CourseInfo=None,
                GroupInfo=None,
                Message=f"Группа '{group_name}' не найдена"
            )
        
        # 2. Получить детали из Neo4j (ID студентов и лекций)
        student_ids, lecture_ids = await self.lecture_repo.get_group_details(group.id)
        
        if not student_ids or not lecture_ids:
            return GroupReportResponse(
                CourseInfo=None,
                GroupInfo=None,
                Message=f"Нет данных для группы '{group_name}' в Neo4j"
            )
        
        # 3. Получить специальные курсы (по департаменту группы)
        courses = await self.course_repo.get_by_lecture_ids_and_department(
            lecture_ids, 
            group.department_id
        )
        
        if not courses:
            return GroupReportResponse(
                CourseInfo=None,
                GroupInfo=None,
                Message=f"Нет специальных курсов для департамента {group.department_id}"
            )
        
        # 4. Получить лекции для этих курсов
        course_ids = [course.id for course in courses]
        lectures = await self.lecture_repo.get_by_course_ids(course_ids)
        
        # Фильтруем только те лекции, которые доступны группе
        lecture_ids_set = set(lecture_ids)
        filtered_lectures = [lec for lec in lectures if lec.id in lecture_ids_set]
        
        if not filtered_lectures:
            return GroupReportResponse(
                CourseInfo=None,
                GroupInfo=None,
                Message=f"Нет лекций для специальных курсов"
            )
        
        # 5. Получить расписание для этих лекций
        filtered_lecture_ids = [lec.id for lec in filtered_lectures]
        schedules = await self.schedule_repo.get_by_lecture_and_group(
            filtered_lecture_ids,
            group.id
        )
        
        # Подсчет общих часов: каждое занятие = 2 часа
        all_hours = len(schedules) * 2
        
        # 6. Получить студентов
        students = await self.student_repo.get_by_ids(student_ids)
        
        # 7. Получить посещения
        schedule_ids = [sched.id for sched in schedules]
        visits = await self.visits_repo.get_by_schedule_and_students(
            schedule_ids,
            student_ids
        )
        
        # 8. Подсчитать посещенные часы для каждого студента
        # Группируем посещения по студентам
        visits_by_student: Dict[int, int] = {}
        for visit in visits:
            visits_by_student[visit.student_id] = visits_by_student.get(visit.student_id, 0) + 1
        
        # 9. Создать DTO для студентов
        student_dtos = []
        for student in students:
            visit_count = visits_by_student.get(student.id, 0)
            visit_hours = visit_count * 2  # каждое посещение = 2 часа
            
            student_dtos.append(StudentDTO(
                student=student,
                all_hours=all_hours,
                visit_hours=visit_hours
            ))
        
        # 10. Формируем ответ
        course_info = CourseDTO(
            courses=courses,
            lectures=filtered_lectures
        )
        
        group_info = GroupDTO(
            group=group,
            students=student_dtos
        )
        
        return GroupReportResponse(
            CourseInfo=course_info,
            GroupInfo=group_info,
            Message=None
        )
