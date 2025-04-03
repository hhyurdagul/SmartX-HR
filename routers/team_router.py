from fastapi import APIRouter, Depends, HTTPException
from models import Team, Project, TeamMember, User
from services.team_service import TeamService
from auth import require_admin_role, require_authenticated_user  # Add require_authenticated_user
from typing import List

router = APIRouter(
    # No single prefix, as endpoints are /teams, /projects, /team_members
    tags=["Teams & Projects"] # Group related features in docs
)

# --- Team Endpoints ---

@router.post("/teams", response_model=Team, status_code=201)
async def create_team(
    team_data: Team,
    team_service: TeamService = Depends(TeamService),
    admin_user: User = Depends(require_admin_role) # Require admin role
):
    """Creates a new team. (Admin Only)"""
    # Service handles validation (e.g., team lead exists)
    return team_service.create_team(team_data)

@router.get("/teams", response_model=List[Team])
async def list_teams(
    team_service: TeamService = Depends(TeamService),
    current_user: User = Depends(require_authenticated_user)
):
    """Retrieves all teams. (Requires Authentication)"""
    return team_service.list_teams()

@router.get("/teams/{team_id}", response_model=Team)
async def get_team(
    team_id: int,
    team_service: TeamService = Depends(TeamService),
    current_user: User = Depends(require_authenticated_user)
):
    """Retrieves a specific team by its ID. (Requires Authentication)"""
    return team_service.get_team(team_id)

@router.get("/teams/{team_id}/members", response_model=List[TeamMember])
async def get_team_members(
    team_id: int,
    team_service: TeamService = Depends(TeamService),
    current_user: User = Depends(require_authenticated_user)
):
    """Retrieves all members belonging to a specific team. (Requires Authentication)"""
    return team_service.get_members_of_team(team_id)


# --- Project Endpoints ---

@router.post("/projects", response_model=Project, status_code=201)
async def create_project(
    project_data: Project,
    team_service: TeamService = Depends(TeamService),
    admin_user: User = Depends(require_admin_role) # Require admin role
):
    """Creates a new project. (Admin Only)"""
    # Service handles validation (e.g., team exists)
    return team_service.create_project(project_data)

@router.get("/projects", response_model=List[Project])
async def list_projects(
    team_id: int | None = None, # Optional query parameter
    team_service: TeamService = Depends(TeamService),
    current_user: User = Depends(require_authenticated_user)
):
    """
    Retrieves projects. Can be filtered by `team_id` using a query parameter.
    (Requires Authentication)
    """
    return team_service.list_projects(team_id=team_id)

@router.get("/projects/{project_id}", response_model=Project)
async def get_project(
    project_id: int,
    team_service: TeamService = Depends(TeamService),
    current_user: User = Depends(require_authenticated_user)
):
    """Retrieves a specific project by its ID. (Requires Authentication)"""
    return team_service.get_project(project_id)


# --- Team Member Endpoints ---

@router.post("/team_members", response_model=TeamMember, status_code=201)
async def add_team_member(
    team_member_data: TeamMember,
    team_service: TeamService = Depends(TeamService),
    admin_user: User = Depends(require_admin_role) # Require admin role
):
    """Adds a user to a team (creates a team membership). (Admin Only)"""
    # Service handles validation (user exists, team exists, user not already in team)
    return team_service.add_user_to_team(team_member_data)

@router.get("/team_members", response_model=List[TeamMember])
async def list_all_team_memberships(
    team_service: TeamService = Depends(TeamService),
    current_user: User = Depends(require_authenticated_user)
):
    """Retrieves all team membership records across all teams. (Requires Authentication)"""
    return team_service.list_all_team_memberships()

@router.get("/team_members/{team_member_id}", response_model=TeamMember)
async def get_team_member_details(
    team_member_id: int,
    team_service: TeamService = Depends(TeamService),
    current_user: User = Depends(require_authenticated_user)
):
    """Retrieves details of a specific team membership entry by its ID. (Requires Authentication)"""
    return team_service.get_team_member_details(team_member_id)

# Endpoint to get teams for a specific user was in original main.py under /users/{user_id}/teams
# Let's keep it consistent with the original structure, maybe move to user_router?
# Or keep it here for team context? Let's add it to user_router for consistency.
# See user_router.py modification needed.