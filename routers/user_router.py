from fastapi import APIRouter, Depends, HTTPException
from models import User, TeamMember # Import TeamMember
from services.user_service import UserService
from services.team_service import TeamService # Import TeamService
from auth import require_admin_role, require_authenticated_user # Import auth dependencies
from typing import List

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