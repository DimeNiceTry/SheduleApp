from typing import List

from elasticsearch import Elasticsearch


class ElasticMaterialsRepository:
    def __init__(self, client: Elasticsearch, index: str = "materials") -> None:
        self._client = client
        self._index = index

    def search_lecture_ids(self, phrase: str, limit: int) -> List[int]:
        if not phrase:
            return []
        response = self._client.search(
            index=self._index,
            size=limit,
            query={
                "match": {
                    "lecture_text": {
                        "query": phrase,
                    }
                }
            },
            source=["id_lect"],
        )
        hits = response.get("hits", {}).get("hits", [])
        lecture_ids = []
        for hit in hits:
            source = hit.get("_source") or {}
            try:
                lecture_id = int(source.get("id_lect"))
            except (TypeError, ValueError):
                continue
            lecture_ids.append(lecture_id)
        return lecture_ids
