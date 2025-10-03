from typing import Iterable, List, Tuple

from neo4j import Driver


class LectureGraphRepository:
    def __init__(self, driver: Driver, database: str = "neo4j") -> None:
        self._driver = driver
        self._database = database

    def get_students_and_groups(self, lecture_ids: Iterable[int]) -> Tuple[List[int], List[int]]:
        ids = [int(i) for i in lecture_ids if i is not None]
        if not ids:
            return [], []
        query = (
            "MATCH (l:Lecture) WHERE l.id IN $LectureIds "
            "OPTIONAL MATCH (s:Student)-[:CAN_ATTEND]->(l) "
            "OPTIONAL MATCH (g:Group)-[:HAS_LECTURE]->(l) "
            "RETURN collect(DISTINCT s.id) AS StudentIds, collect(DISTINCT g.id) AS GroupIds"
        )
        with self._driver.session(database=self._database) as session:
            record = session.run(query, LectureIds=ids).single()
        student_ids = [int(i) for i in record["StudentIds"] or [] if i is not None]
        group_ids = [int(i) for i in record["GroupIds"] or [] if i is not None]
        return student_ids, group_ids
