from collections import defaultdict
from datetime import datetime
from typing import List

from ..config import get_settings
from ..repositories.elastic_repository import ElasticMaterialsRepository
from ..repositories.neo4j_repository import LectureGraphRepository
from ..repositories.schedule_repository import ScheduleRepository
from ..repositories.student_repository import StudentRepository
from ..repositories.visits_repository import VisitsRepository


class LowAttendanceReportService:
    def __init__(
        self,
        elastic_repo: ElasticMaterialsRepository,
        lecture_repo: LectureGraphRepository,
        schedule_repo: ScheduleRepository,
        visits_repo: VisitsRepository,
        student_repo: StudentRepository,
    ) -> None:
        self._elastic_repo = elastic_repo
        self._lecture_repo = lecture_repo
        self._schedule_repo = schedule_repo
        self._visits_repo = visits_repo
        self._student_repo = student_repo
        self._settings = get_settings()

    def get_report(self, search_term: str, start: datetime, end: datetime) -> List[dict]:
        limit = self._settings.report_limit
        lecture_ids = self._elastic_repo.search_lecture_ids(search_term, self._settings.elastic_search_limit)
        if not lecture_ids:
            return []
        student_ids, group_ids = self._lecture_repo.get_students_and_groups(lecture_ids)
        if not student_ids or not group_ids:
            return []

        schedules = self._schedule_repo.fetch(lecture_ids, group_ids, start, end)
        if not schedules:
            return []
        schedule_ids = [row["id"] for row in schedules]
        visits = self._visits_repo.fetch_by_schedule(schedule_ids)
        students = self._student_repo.fetch_many(student_ids)
        if not students:
            return []
        students_by_id = {student["id"]: student for student in students}

        lectures_per_group = defaultdict(int)
        for schedule in schedules:
            lectures_per_group[schedule["group_id"]] += 1

        visits_by_student = defaultdict(set)
        for visit in visits:
            visits_by_student[visit["student_id"]].add(visit["schedule_id"])

        report_items: List[dict] = []
        for student_id, student in students_by_id.items():
            group_id = student.get("group_id")
            total = lectures_per_group.get(group_id, 0)
            attended = len(visits_by_student.get(student_id, set()))
            percentage = round((attended / total) * 100.0, 2) if total else 0.0
            report_items.append(
                {
                    "student": student,
                    "attendance_percentage": percentage,
                    "attended_lectures": attended,
                    "total_lectures": total,
                    "report_start": start.isoformat(),
                    "report_end": end.isoformat(),
                    "search_term": search_term,
                }
            )

        report_items.sort(key=lambda item: item["attendance_percentage"])
        return report_items[:limit]
