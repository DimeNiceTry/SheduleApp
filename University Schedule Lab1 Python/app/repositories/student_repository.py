from datetime import datetime
from typing import Dict, Iterable, List, Optional

import redis


class StudentRepository:
    def __init__(self, client: redis.Redis, key_prefix: str = "student:") -> None:
        self._client = client
        self._key_prefix = key_prefix

    def fetch_many(self, ids: Iterable[int]) -> List[dict]:
        distinct_ids = sorted({int(i) for i in ids if i is not None})
        students: List[dict] = []
        for student_id in distinct_ids:
            key = f"{self._key_prefix}{student_id}"
            data = self._client.hgetall(key)
            if not data:
                continue
            student = self._deserialize(student_id, data)
            if student:
                students.append(student)
        return students

    def _deserialize(self, student_id: int, data: Dict[str, str]) -> Optional[dict]:
        try:
            full_name = data.get("full_name") or data.get("fio")
            if not full_name:
                return None
            group_id = int(data.get("id_group")) if data.get("id_group") is not None else None
            date_raw = data.get("date_of_recipient")
            date_of_recipient: Optional[str]
            if date_raw:
                try:
                    parsed = datetime.strptime(date_raw, "%Y-%m-%d").date()
                except ValueError:
                    parsed = datetime.fromisoformat(date_raw).date()
                date_of_recipient = parsed.isoformat()
            else:
                date_of_recipient = None
            return {
                "id": student_id,
                "full_name": full_name,
                "group_id": group_id,
                "date_of_recipient": date_of_recipient,
            }
        except Exception:
            return None
