from elasticsearch import AsyncElasticsearch

class ElasticHandler:
    def __init__(self):
        self.es = AsyncElasticsearch("http://elasticsearch:9200")

    async def create_index(self, index_name="courses"):
        """Создание индекса согласно схеме elasticsearch.json"""
        mapping = {
            "mappings": {
                "properties": {
                    "id": {
                        "type": "integer"
                    },
                    "name": {
                        "type": "text",
                        "analyzer": "russian",
                        "fields": {
                            "keyword": {
                                "type": "keyword"
                            }
                        }
                    },
                    "description": {
                        "type": "text", 
                        "analyzer": "russian"
                    },
                    "term": {
                        "type": "text"
                    },
                    "department": {
                        "type": "text",
                        "analyzer": "russian"
                    },
                    "specialty": {
                        "type": "text", 
                        "analyzer": "russian"
                    },
                    "requirments": {
                        "type": "boolean"
                    }
                }
            },
            "settings": {
                "analysis": {
                    "analyzer": {
                        "russian": {
                            "tokenizer": "standard",
                            "filter": ["lowercase", "russian_stop", "russian_stemmer"]
                        }
                    },
                    "filter": {
                        "russian_stop": {
                            "type": "stop",
                            "stopwords": "_russian_"
                        },
                        "russian_stemmer": {
                            "type": "stemmer",
                            "language": "russian"
                        }
                    }
                }
            }
        }
        
        try:
            await self.es.indices.create(index=index_name, body=mapping)
        except Exception:
            pass  # Индекс уже существует

    async def create_initial_course(self):
        """Создание начального курса согласно схеме elasticsearch.json"""
        await self.create_index()
        
        initial_course = {
            "id": 1,
            "name": "Проектирование архитектуры программного обеспечения",
            "description": "Курс посвящен изучению принципов и методов проектирования архитектуры программного обеспечения. Рассматриваются различные архитектурные паттерны, принципы SOLID, микросервисная архитектура.",
            "term": "2025-2026",
            "department": "Факультет разработки ПО", 
            "specialty": "Информационные системы и технологии",
            "requirments": True
        }
        
        await self.es.index(
            index="courses",
            id=initial_course["id"],
            document=initial_course
        )
        return initial_course

    async def index_courses(self, courses):
        """Индексация курсов согласно новой схеме"""
        await self.create_index()
        
        for c in courses:
            document = {
                "id": c["id"],
                "name": c.get("name", c.get("title", "")),
                "description": c.get("desc", c.get("description", "")),
                "term": c.get("term", "2025-2026"),
                "department": "Факультет разработки ПО",
                "specialty": "Информационные системы и технологии",
                "requirments": True
            }
            
            await self.es.index(
                index="courses", 
                id=c["id"], 
                document=document
            )

    async def get_course(self, course_id):
        """Получение курса по ID"""
        try:
            result = await self.es.get(index="courses", id=course_id)
            return result["_source"]
        except Exception:
            return None

    async def search_courses(self, query, size=10):
        """Полнотекстовый поиск курсов согласно новой схеме"""
        search_body = {
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": ["name^3", "description^2", "department", "specialty"],
                    "type": "best_fields"
                }
            },
            "highlight": {
                "fields": {
                    "name": {},
                    "description": {},
                    "department": {},
                    "specialty": {}
                }
            },
            "size": size
        }
        
        result = await self.es.search(index="courses", body=search_body)
        return result["hits"]["hits"]

    async def update_course(self, course_id, updated_data):
        """Обновление курса"""
        try:
            await self.es.update(
                index="courses",
                id=course_id,
                body={"doc": updated_data}
            )
            return True
        except Exception:
            return False

    async def delete_course(self, course_id):
        """Удаление курса"""
        try:
            await self.es.delete(index="courses", id=course_id)
            return True
        except Exception:
            return False

    async def get_all_courses(self):
        """Получение всех курсов"""
        search_body = {
            "query": {"match_all": {}},
            "size": 1000
        }
        
        result = await self.es.search(index="courses", body=search_body)
        return [hit["_source"] for hit in result["hits"]["hits"]]

    async def delete_index(self, index_name="courses"):
        """Удаление индекса"""
        try:
            await self.es.indices.delete(index=index_name)
            return True
        except Exception:
            return False

    async def check_connection(self):
        """Проверка доступности Elasticsearch"""
        try:
            await self.es.ping()
            return True
        except Exception:
            return False

    async def close(self):
        """Закрытие соединения"""
        await self.es.close()
