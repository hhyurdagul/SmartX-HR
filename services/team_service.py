from models import Team, Project, TeamMember, User
from repositories.team_repository import TeamRepository
from repositories.user_repository import UserRepository # To validate user IDs
from fastapi import Depends, HTTPException
from typing import List

class TeamService:
    """Encapsulates business logic related to Teams, Projects, and Team Members."""

    def __init__(
        self,
        team_repository: TeamRepository = Depends(),
        user_repository: UserRepository = Depends()
    ):
        self.team_repository = team_repository
        self.user_repository = user_repository

    def _check_user_exists(self, user_id: int | None):
        """Helper to check if a user exists, raising HTTPException if not."""
        if user_id is None:
            return None # Allow optional user IDs (e.g., team lead)
        user = self.user_repository.get_user_by_id(user_id)
        if user is None:
            raise HTTPException(status_code=404, detail=f"User with ID {user_id} not found")
        return user

    def _check_team_exists(self, team_id: int | None):
        """Helper to check if a Team exists."""
        if team_id is None:
            return None # Allow optional team IDs (e.g., project team)
        team = self.team_repository.get_team_by_id(team_id)
        if team is None:
            raise HTTPException(status_code=404, detail=f"Team with ID {team_id} not found")
        return team

    def _check_project_exists(self, project_id: int):
        """Helper to check if a Project exists."""
        project = self.team_repository.get_project_by_id(project_id)
        if project is None:
            raise HTTPException(status_code=404, detail=f"Project with ID {project_id} not found")
        return project

    # --- Team Methods ---

    def create_team(self, team_data: Team) -> Team:
        """Creates a new team."""
        if team_data.team_lead_user_id:
            self._check_user_exists(team_data.team_lead_user_id) # Validate team lead if provided
        try:
            return self.team_repository.create_team(team_data)
        except Exception as e:
            print(f"Error creating team in service: {e}")
            raise HTTPException(status_code=500, detail="Failed to create team.")

    def get_team(self, team_id: int) -> Team:
        """Retrieves a specific team."""
        team = self.team_repository.get_team_by_id(team_id)
        if team is None:
            raise HTTPException(status_code=404, detail=f"Team with ID {team_id} not found")
        return team

    def list_teams(self) -> List[Team]:
        """Retrieves all teams."""
        return self.team_repository.list_teams()

    # --- Project Methods ---

    def create_project(self, project_data: Project) -> Project:
        """Creates a new project."""
        if project_data.team_id:
            self._check_team_exists(project_data.team_id) # Validate team if provided
        # Add validation for dates, status, etc.
        allowed_statuses = ["planning", "in_progress", "completed", "on_hold"]
        if project_data.status not in allowed_statuses:
             project_data.status = "planning" # Default or raise error

        try:
            return self.team_repository.create_project(project_data)
        except Exception as e:
            print(f"Error creating project in service: {e}")
            raise HTTPException(status_code=500, detail="Failed to create project.")

    def get_project(self, project_id: int) -> Project:
        """Retrieves a specific project."""
        project = self.team_repository.get_project_by_id(project_id)
        if project is None:
            raise HTTPException(status_code=404, detail=f"Project with ID {project_id} not found")
        return project

    def list_projects(self, team_id: int | None = None) -> List[Project]:
        """Retrieves projects, optionally filtered by team."""
        if team_id is not None:
            self._check_team_exists(team_id) # Validate team if provided
        return self.team_repository.list_projects(team_id=team_id)

    # --- Team Member Methods ---

    def add_user_to_team(self, team_member_data: TeamMember) -> TeamMember:
        """Adds a user to a team."""
        self._check_user_exists(team_member_data.user_id)
        self._check_team_exists(team_member_data.team_id)
        # Add validation: check role_in_team?

        try:
            created_member = self.team_repository.create_team_member(team_member_data)
            if created_member is None:
                 # This happens if the user is already in the team (IntegrityError caught in repo)
                 raise HTTPException(status_code=400, detail=f"User {team_member_data.user_id} is already a member of team {team_member_data.team_id}.")
            return created_member
        except Exception as e:
            print(f"Error adding team member in service: {e}")
            raise HTTPException(status_code=500, detail="Failed to add user to team.")

    def get_team_member_details(self, team_member_id: int) -> TeamMember:
        """Retrieves details of a specific team membership entry."""
        member = self.team_repository.get_team_member_by_id(team_member_id)
        if member is None:
            raise HTTPException(status_code=404, detail=f"Team Member entry with ID {team_member_id} not found")
        return member

    def list_all_team_memberships(self) -> List[TeamMember]:
        """Retrieves all team membership entries."""
        return self.team_repository.list_team_members()

    def get_members_of_team(self, team_id: int) -> List[TeamMember]:
        """Retrieves all members for a specific team."""
        self._check_team_exists(team_id) # Ensure team exists
        return self.team_repository.get_members_by_team_id(team_id)

    def get_teams_for_user(self, user_id: int) -> List[TeamMember]:
        """Retrieves all teams a specific user belongs to."""
        self._check_user_exists(user_id) # Ensure user exists
        return self.team_repository.get_teams_for_user_id(user_id)

    # Add update/delete methods as needed (e.g., remove_user_from_team, update_member_role)