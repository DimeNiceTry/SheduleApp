from datetime import datetime

from pydantic import BaseModel, Field


class FindBadStudentsRequest(BaseModel):
    search_term: str = Field(..., alias="searchTerm")
    start_date: datetime = Field(..., alias="startDate")
    end_date: datetime = Field(..., alias="endDate")

    class Config:
        allow_population_by_field_name = True
        json_schema_extra = {
            "example": {
                "searchTerm": "linear algebra",
                "startDate": "2025-09-01T00:00:00Z",
                "endDate": "2026-01-31T23:59:59Z",
            }
        }
