from pydantic import BaseModel
from typing import Optional

class User(BaseModel):
    user_id: Optional[int] = None
    username: str
    email: str
    role: str # e.g., "employee", "manager"
    start_date: str # YYYY-MM-DD

class LeaveRequest(BaseModel):
    leave_request_id: Optional[int] = None
    user_id: int
    leave_type: str # e.g., "Yıllık İzin", "Hastalık İzni"
    start_date: str # YYYY-MM-DD
    end_date: str # YYYY-MM-DD
    reason: str
    status: str = "pending" # "pending", "approved", "rejected"

class LeaveBalance(BaseModel):
    leave_balance_id: Optional[int] = None # Add ID for database
    user_id: int
    total_days: int
    used_days: int
    remaining_days: int

# KPI Feature Models
class KPICategory(BaseModel):
    category_id: Optional[int] = None
    category_name: str

class KPI(BaseModel):
    kpi_id: Optional[int] = None
    category_id: int
    kpi_name: str
    unit: str
    description: Optional[str] = None

class KPIResult(BaseModel):
    result_id: Optional[int] = None
    kpi_id: int
    user_id: int
    period: str # "2024-1.Dönem"
    target: int
    actual_value: int

# Training Feature Models
class TrainingCategory(BaseModel):
    training_category_id: Optional[int] = None
    training_category_name: str

class TrainingCourse(BaseModel):
    training_course_id: Optional[int] = None
    training_category_id: int
    course_name: str
    description: Optional[str] = None
    duration_hours: int

class UserTrainingProgress(BaseModel):
    progress_id: Optional[int] = None
    user_id: int
    training_course_id: int
    enrollment_date: str # YYYY-MM-DD
    completion_percentage: float = 0.0
    is_completed: bool = False


# Team Feature Models
class Team(BaseModel):
    team_id: Optional[int] = None
    team_name: str
    description: Optional[str] = None
    team_lead_user_id: Optional[int] = None # FK to Users table

class Project(BaseModel):
    project_id: Optional[int] = None
    project_name: str
    description: Optional[str] = None
    start_date: str # YYYY-MM-DD
    end_date: str # YYYY-MM-DD
    team_id: Optional[int] = None # FK to Teams table
    status: str = "planning" # e.g., "planning", "in_progress", "completed", "on_hold"

class TeamMember(BaseModel): # For Team-User relationship
    team_member_id: Optional[int] = None
    team_id: int
    user_id: int
    role_in_team: Optional[str] = None # e.g., "Developer", "Tester", "Analyst"