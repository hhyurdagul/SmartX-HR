from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from models import User, LeaveRequest, LeaveBalance, KPI, KPICategory, KPIResult, TrainingCategory, TrainingCourse, UserTrainingProgress, Team, Project, TeamMember # Import models
import db_utils # Import db utility functions

app = FastAPI()

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    db_utils.initialize_database()

# --- User Endpoints (Example - adapted for DB) ---
@app.get("/users/me", response_model=User)
async def get_current_user():
    """Simulates getting the current user from the database."""
    user = db_utils.get_user_by_id_db(1) # Assuming user_id 1 is "me"
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# --- Leave Request Endpoints (Adapted for DB) ---
@app.post("/leaves/requests", response_model=LeaveRequest, status_code=201)
async def create_leave_request(leave_request: LeaveRequest):
    return db_utils.create_leave_request_db(leave_request)

@app.get("/leaves/requests", response_model=List[LeaveRequest])
async def list_leave_requests():
    return db_utils.list_leave_requests_db()

@app.get("/leaves/requests/{leave_request_id}", response_model=LeaveRequest)
async def get_leave_request(leave_request_id: int):
    leave_request = db_utils.get_leave_request_db(leave_request_id)
    if leave_request is None:
        raise HTTPException(status_code=404, detail="Leave request not found")
    return leave_request

@app.put("/leaves/requests/{leave_request_id}", response_model=LeaveRequest)
async def update_leave_request(leave_request_id: int, update_request: LeaveRequest):
    leave_request = db_utils.get_leave_request_db(leave_request_id)
    if leave_request is None:
        raise HTTPException(status_code=404, detail="Leave request not found")
    updated_request = db_utils.update_leave_request_status_db(leave_request_id, update_request.status) # Specific status update function
    return updated_request

# --- Leave Balance Endpoints (Adapted for DB) ---
@app.get("/leaves/balance/me", response_model=LeaveBalance)
async def get_my_leave_balance():
    current_user = await get_current_user()
    leave_balance = db_utils.get_leave_balance_by_user_id_db(current_user.user_id)
    if leave_balance is None:
        raise HTTPException(status_code=404, detail="Leave balance not found")
    return leave_balance

# --- KPI Category Endpoints ---
@app.post("/kpi/categories", response_model=KPICategory, status_code=201)
async def create_kpi_category(category: KPICategory):
    return db_utils.create_kpi_category_db(category)

@app.get("/kpi/categories", response_model=List[KPICategory])
async def list_kpi_categories():
    return db_utils.list_kpi_categories_db()

@app.get("/kpi/categories/{category_id}", response_model=KPICategory)
async def get_kpi_category(category_id: int):
    category = db_utils.get_kpi_category_db(category_id)
    if category is None:
        raise HTTPException(status_code=404, detail="KPI Category not found")
    return category

# --- KPI Endpoints ---
@app.post("/kpis", response_model=KPI, status_code=201)
async def create_kpi(kpi: KPI):
    return db_utils.create_kpi_db(kpi)

@app.get("/kpis", response_model=List[KPI])
async def list_kpis():
    return db_utils.list_kpis_db()

@app.get("/kpis/{kpi_id}", response_model=KPI)
async def get_kpi(kpi_id: int):
    kpi = db_utils.get_kpi_db(kpi_id)
    if kpi is None:
        raise HTTPException(status_code=404, detail="KPI not found")
    return kpi

# --- KPI Result Endpoints ---
@app.post("/kpi/results", response_model=KPIResult, status_code=201)
async def create_kpi_result(result: KPIResult):
    return db_utils.create_kpi_result_db(result)

@app.get("/kpi/results", response_model=List[KPIResult])
async def list_kpi_results():
    return db_utils.list_kpi_results_db()

@app.get("/kpi/results/{result_id}", response_model=KPIResult)
async def get_kpi_result(result_id: int):
    result = db_utils.get_kpi_result_db(result_id)
    if result is None:
        raise HTTPException(status_code=404, detail="KPI Result not found")
    return result

# --- Training Category Endpoints ---
@app.post("/training/categories", response_model=TrainingCategory, status_code=201)
async def create_training_category(category: TrainingCategory):
    return db_utils.create_training_category_db(category)

@app.get("/training/categories", response_model=List[TrainingCategory])
async def list_training_categories():
    return db_utils.list_training_categories_db()

@app.get("/training/categories/{category_id}", response_model=TrainingCategory)
async def get_training_category(category_id: int):
    category = db_utils.get_training_category_db(category_id)
    if category is None:
        raise HTTPException(status_code=404, detail="Training Category not found")
    return category

# --- Training Course Endpoints ---
@app.post("/training/courses", response_model=TrainingCourse, status_code=201)
async def create_training_course(course: TrainingCourse):
    return db_utils.create_training_course_db(course)

@app.get("/training/courses", response_model=List[TrainingCourse])
async def list_training_courses():
    return db_utils.list_training_courses_db()

@app.get("/training/courses/{course_id}", response_model=TrainingCourse)
async def get_training_course(course_id: int):
    course = db_utils.get_training_course_db(course_id)
    if course is None:
        raise HTTPException(status_code=404, detail="Training Course not found")
    return course

# --- User Training Progress Endpoints ---
@app.post("/training/progress", response_model=UserTrainingProgress, status_code=201)
async def create_user_training_progress(progress: UserTrainingProgress):
    return db_utils.create_user_training_progress_db(progress)

@app.get("/training/progress", response_model=List[UserTrainingProgress])
async def list_user_training_progress():
    return db_utils.list_user_training_progress_db()

@app.get("/training/progress/{progress_id}", response_model=UserTrainingProgress)
async def get_user_training_progress(progress_id: int):
    progress = db_utils.get_user_training_progress_db(progress_id)
    if progress is None:
        raise HTTPException(status_code=404, detail="User Training Progress not found")
    return progress

@app.put("/training/progress/{progress_id}", response_model=UserTrainingProgress)
async def update_user_training_progress(progress_id: int, progress_update: dict):
    progress = db_utils.get_user_training_progress_db(progress_id)
    if progress is None:
        raise HTTPException(status_code=404, detail="User Training Progress not found")
    updated_progress = db_utils.update_user_training_progress_db(progress_id, progress_update)
    return updated_progress

# --- Team Endpoints ---
@app.post("/teams", response_model=Team, status_code=201)
async def create_team(team: Team):
    return db_utils.create_team_db(team)

@app.get("/teams", response_model=List[Team])
async def list_teams():
    return db_utils.list_teams_db()

@app.get("/teams/{team_id}", response_model=Team)
async def get_team(team_id: int):
    team = db_utils.get_team_db(team_id)
    if team is None:
        raise HTTPException(status_code=404, detail="Team not found")
    return team

# --- Project Endpoints ---
@app.post("/projects", response_model=Project, status_code=201)
async def create_project(project: Project):
    return db_utils.create_project_db(project)

@app.get("/projects", response_model=List[Project])
async def list_projects():
    return db_utils.list_projects_db()

@app.get("/projects/{project_id}", response_model=Project)
async def get_project(project_id: int):
    project = db_utils.get_project_db(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

# --- Team Member Endpoints ---
@app.post("/team_members", response_model=TeamMember, status_code=201)
async def create_team_member(team_member: TeamMember):
    created_member = db_utils.create_team_member_db(team_member)
    if created_member is None:
        raise HTTPException(status_code=400, detail="User is already a member of this team.") # Or other appropriate error
    return created_member

@app.get("/team_members", response_model=List[TeamMember])
async def list_team_members():
    return db_utils.list_team_members_db()

@app.get("/team_members/{team_member_id}", response_model=TeamMember)
async def get_team_member(team_member_id: int):
    team_member = db_utils.get_team_member_db(team_member_id)
    if team_member is None:
        raise HTTPException(status_code=404, detail="Team Member not found")
    return team_member

@app.get("/teams/{team_id}/members", response_model=List[TeamMember])
async def get_team_members_by_team(team_id: int):   
    if db_utils.get_team_db(team_id) is None: # Ensure team exists
        raise HTTPException(status_code=404, detail="Team not found")
    return db_utils.get_team_members_by_team_id_db(team_id)

@app.get("/users/{user_id}/teams", response_model=List[TeamMember])
async def get_teams_for_user(user_id: int):
    if db_utils.get_user_by_id_db(user_id) is None: # Ensure user exists
        raise HTTPException(status_code=404, detail="User not found")
    return db_utils.get_teams_for_user_db(user_id)