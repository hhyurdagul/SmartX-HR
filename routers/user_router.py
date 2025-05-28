from fastapi import APIRouter, Depends, HTTPException
from models import User, TeamMember, KPIResult, UserTrainingProgress, TrainingCourse # Updated models
from services.user_service import UserService
from services.team_service import TeamService
from services.kpi_service import KpiService # Added KpiService
from services.training_service import TrainingService # Added TrainingService
from services.ai_service import AIService # Added AIService
from auth import require_admin_role, require_authenticated_user # Import auth dependencies
from typing import List, Dict # Added Dict
import asyncio # Added asyncio

router = APIRouter(
    prefix="/users", # All routes in this file will start with /users
    tags=["Users"]   # Tag for OpenAPI documentation
)

# Example: Endpoint to get the 'current' user (simulated as user_id 1)
# Note: In a real app, this dependency would provide the actual current user
@router.get("/me", response_model=User)
async def get_current_user(
    current_user: User = Depends(require_authenticated_user) # Require authentication
):
    """
    Retrieves the details for the currently authenticated user.
    """
    # The require_authenticated_user dependency already provides the user object.
    return current_user

# Example: Endpoint to create a user (Admin Only)
@router.post("/", response_model=User, status_code=201)
async def create_new_user(
    user_data: User,
    user_service: UserService = Depends(UserService),
    admin_user: User = Depends(require_admin_role) # Require admin role
):
    """
    Creates a new user. (Admin Only)
    """
    # The service handles creation logic, validation, and potential errors
    # The require_admin_role dependency ensures only admins reach this point
    print(f"Admin user {admin_user.username} creating new user: {user_data.username}") # Optional logging
    return user_service.create_new_user(user_data)

# Add other user-specific endpoints here (e.g., get user by ID, list users)
# Example: Get user by specific ID (Requires Authentication)
@router.get("/{user_id}", response_model=User)
async def get_user_by_id(
    user_id: int,
    user_service: UserService = Depends(UserService),
    current_user: User = Depends(require_authenticated_user) # Require authentication
):
    """
    Retrieves details for a specific user by their ID. (Requires Authentication)
    """
    return user_service.get_user(user_id)

# Endpoint to get teams for a specific user
@router.get("/{user_id}/teams", response_model=List[TeamMember])
async def get_teams_for_user(
    user_id: int,
    team_service: TeamService = Depends(TeamService), # Inject TeamService
    current_user: User = Depends(require_authenticated_user) # Require authentication
):
    """
    Retrieves all team memberships for a specific user. (Requires Authentication)
    """
    # The TeamService handles checking if the user exists and fetching the data
    return team_service.get_teams_for_user(user_id)

@router.get("/{user_id}/ai-training-recommendations", response_model=Dict, tags=["Users", "AI Recommendations"])
async def get_ai_training_recommendations(
    user_id: int,
    current_user: User = Depends(require_authenticated_user),
    ai_service: AIService = Depends(),
    user_service: UserService = Depends(),
    kpi_service: KpiService = Depends(),
    training_service: TrainingService = Depends()
):
    """
    Provides AI-generated training course recommendations for a specified user.

    This endpoint generates personalized training recommendations for a user based on
    their profile information, Key Performance Indicators (KPIs), past completed
    trainings, and the list of all available courses in the system.
    The AI can suggest existing courses or propose new course ideas if suitable.

    Path Parameter:
    - `user_id`: The ID of the user for whom recommendations are being requested.

    Authentication:
    - A user can request recommendations for themselves.
    - An admin user can request recommendations for any user.

    Process:
    1. Verifies if the requesting user is authorized (self or admin).
    2. Fetches the specified user's details (profile, KPIs, past trainings).
    3. Fetches all available training courses.
    4. Sends this compiled data to an AI service.
    5. The AI service analyzes the data and returns tailored training recommendations.

    Returns:
    A dictionary containing:
    - `recommendations`: A list of recommended course objects. Each object includes
      `course_id_or_idea` (can be an existing course ID or "New Course Idea"),
      `course_name` (name of existing course or new idea), and `reasoning`.
    - `error_message`: A string describing an error if one occurred during the
      AI processing or data fetching, otherwise `None`.
    """
    # 3. Authorization
    if not (current_user.user_id == user_id or current_user.role == 'admin'):
        raise HTTPException(status_code=403, detail="Not authorized to request recommendations for this user.")

    # 4. Data Fetching Logic
    # User Details
    user_details_model = await asyncio.to_thread(user_service.user_repository.get_user_by_id, user_id)
    if not user_details_model:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_details_dict = user_details_model.dict()
    # Assuming 'career_goals' is an optional field in User model. If it exists and is None,
    # .dict() will handle it. If it's not part of User model, AIService prompt needs adjustment or pass 'N/A'.
    # For this implementation, we assume it might exist or be None.
    # If User model has a specific field like `career_goals: Optional[str] = None`
    # user_details_dict['career_goals'] = user_details_model.career_goals 
    # If not, the AIService prompt should use .get('career_goals', 'N/A')

    # User KPIs
    user_kpis_models = await asyncio.to_thread(kpi_service.kpi_repository.list_results_for_user, user_id=user_id)
    user_kpis_list = []
    if user_kpis_models: # list_results_for_user might return None or empty list
        # Need to fetch KPI names if list_results only gives kpi_id
        for kpi_res in user_kpis_models:
            kpi_def = await asyncio.to_thread(kpi_service.kpi_repository.get_kpi_by_id, kpi_res.kpi_id)
            kpi_data = kpi_res.dict()
            kpi_data['kpi_name'] = kpi_def.kpi_name if kpi_def else "Unknown KPI"
            user_kpis_list.append(kpi_data)
            
    # User Completed Trainings
    user_training_progress_models = await asyncio.to_thread(training_service.training_repository.list_progress_for_user, user_id=user_id)
    user_completed_trainings_list = []
    if user_training_progress_models: # list_progress_for_user might return None or empty list
        for progress_item in user_training_progress_models:
            if progress_item.is_completed:
                course_model = await asyncio.to_thread(training_service.training_repository.get_course_by_id, progress_item.training_course_id)
                user_completed_trainings_list.append({
                    "course_name": course_model.course_name if course_model else "Unknown Course",
                    "completion_percentage": progress_item.completion_percentage, # AIService might not need this if is_completed=True
                    "enrollment_date": progress_item.enrollment_date # As proxy for completion date
                })

    # All Available Courses
    all_courses_models = await asyncio.to_thread(training_service.training_repository.list_courses)
    all_courses_list = [course.dict() for course in all_courses_models] if all_courses_models else []

    # 5. Call AIService
    recommendation_result = await ai_service.recommend_training_courses(
        user_details_dict,
        user_kpis_list,
        user_completed_trainings_list,
        all_courses_list
    )

    # 6. Return Result
    # If recommendation_result.get("error_message"), FastAPI will still return 200 OK with the error in body.
    # This is acceptable per subtask. Could add specific error raising:
    # if recommendation_result.get("error_message"):
    #     raise HTTPException(status_code=500, detail=f"AI Service Error: {recommendation_result.get('error_message')}")
    return recommendation_result