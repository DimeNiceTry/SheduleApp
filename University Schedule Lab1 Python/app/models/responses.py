from pydantic import BaseModel, Field


class StudentInfo(BaseModel):
    id: int = Field(..., description="Student identifier")
    full_name: str = Field(..., description="Student full name")
    group_id: int | None = Field(None, description="Group identifier")
    date_of_recipient: str | None = Field(None, description="Enrollment date in ISO format")


class LowAttendanceItem(BaseModel):
    student: StudentInfo
    attendance_percentage: float = Field(..., ge=0, le=100, description="Attendance percentage for the period")
    attended_lectures: int = Field(..., ge=0, description="Number of attended lectures")
    total_lectures: int = Field(..., ge=0, description="Total lectures in the period")
    report_start: str = Field(..., description="Report period start in ISO format")
    report_end: str = Field(..., description="Report period end in ISO format")
    search_term: str = Field(..., description="Matched term or phrase")


class LowAttendanceResponse(BaseModel):
    results: list[LowAttendanceItem]
