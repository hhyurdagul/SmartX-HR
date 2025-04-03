from fastapi import APIRouter, Depends, HTTPException, Body
from models import TrainingCourse, UserTrainingProgress, User
from services.training_service import TrainingService
from auth import require_admin_role, require_authenticated_user
from typing import List, Dict, Any

router = APIRouter(
    prefix="/training", # Base prefix for training routes
    tags=["Training"]   # Tag for OpenAPI documentation
)

# --- Training Course Endpoints ---

@router.post("/courses", response_model=TrainingCourse, status_code=201)
async def create_training_course(
    course_data: TrainingCourse,
    training_service: TrainingService = Depends(TrainingService),
    admin_user: User = Depends(require_admin_role) # Require admin role
):
    """Creates a new training course. (Admin Only)"""
    # Service handles validation (e.g., category exists)
    return training_service.create_training_course(course_data)

@router.get("/courses", response_model=List[TrainingCourse])
async def list_training_courses(
    category_id: int | None = None, # Optional query parameter
    training_service: TrainingService = Depends(TrainingService),
    current_user: User = Depends(require_authenticated_user)
):
    """
    Retrieves training courses. Can be filtered by `category_id`
    using a query parameter (e.g., `/training/courses?category_id=1`).
    (Requires Authentication)
    """
    return training_service.list_training_courses(category_id=category_id)

@router.get("/courses/{course_id}", response_model=TrainingCourse)
async def get_training_course(
    course_id: int,
    training_service: TrainingService = Depends(TrainingService),
    current_user: User = Depends(require_authenticated_user)
):
    """Retrieves a specific training course by its ID. (Requires Authentication)"""
    return training_service.get_training_course(course_id)


# --- User Training Progress Endpoints ---

@router.post("/progress", response_model=UserTrainingProgress, status_code=201)
async def create_user_training_progress(
    progress_data: UserTrainingProgress,
    training_service: TrainingService = Depends(TrainingService)
):
    """Enrolls a user in a training course or records initial progress."""
    # Service handles validation (user exists, course exists, etc.)
    return training_service.create_user_training_progress(progress_data)

@router.get("/progress", response_model=List[UserTrainingProgress])
async def list_user_training_progress(
    user_id: int | None = None,    # Optional query parameter
    course_id: int | None = None, # Optional query parameter
    training_service: TrainingService = Depends(TrainingService),
    current_user: User = Depends(require_authenticated_user)
):
    """
    Retrieves user training progress records. Can be filtered by `user_id`
    and/or `course_id` using query parameters. (Requires Authentication)
    """
    return training_service.list_user_training_progress(user_id=user_id, course_id=course_id)

@router.get("/progress/{progress_id}", response_model=UserTrainingProgress)
async def get_user_training_progress(
    progress_id: int,
    training_service: TrainingService = Depends(TrainingService),
    current_user: User = Depends(require_authenticated_user)
):
    """Retrieves a specific user training progress record by its ID. (Requires Authentication)"""
    return training_service.get_user_training_progress(progress_id)

@router.put("/progress/{progress_id}", response_model=UserTrainingProgress)
async def update_user_training_progress(
    progress_id: int,
    progress_update_data: Dict[str, Any] = Body(..., example={"completion_percentage": 50.5}),
    training_service: TrainingService = Depends(TrainingService),
    admin_user: User = Depends(require_admin_role) # Require admin role
):
    """
    Updates a user's training progress (e.g., completion percentage). (Admin Only)
    Expects a JSON body with fields to update, like: `{"completion_percentage": 75}`
    """
    if not progress_update_data:
         raise HTTPException(status_code=400, detail="Request body cannot be empty for update.")
    # Service handles validation and update logic
    return training_service.update_user_training_progress(progress_id, progress_update_data)