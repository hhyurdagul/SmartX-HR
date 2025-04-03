from models import Team, Project, TeamMember
from .base_repository import get_db_connection
from typing import List
import sqlite3

class TeamRepository:
    """Handles database operations for Team, Project, and TeamMember entities."""

    # --- Team Methods ---

    def create_team(self, team: Team) -> Team:
        """Creates a new team."""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO teams (team_name, description, team_lead_user_id) VALUES (?, ?, ?)",
                    (team.team_name, team.description, team.team_lead_user_id),
                )
                conn.commit()
                team_id = cursor.lastrowid
                return Team(team_id=team_id, **team.dict(exclude={'team_id'}))
        except sqlite3.Error as e:
            print(f"Database Error creating team: {e}")
            raise

    def list_teams(self) -> List[Team]:
        """Retrieves all teams."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM teams ORDER BY team_name")
            rows = cursor.fetchall()
            return [Team(**dict(row)) for row in rows]

    def get_team_by_id(self, team_id: int) -> Team | None:
        """Retrieves a team by its ID."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM teams WHERE team_id = ?", (team_id,))
            row = cursor.fetchone()
            if row:
                return Team(**dict(row))
            return None

    # --- Project Methods ---

    def create_project(self, project: Project) -> Project:
        """Creates a new project."""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO projects (project_name, description, start_date, end_date, team_id, status) VALUES (?, ?, ?, ?, ?, ?)",
                    (project.project_name, project.description, project.start_date, project.end_date, project.team_id, project.status),
                )
                conn.commit()
                project_id = cursor.lastrowid
                return Project(project_id=project_id, **project.dict(exclude={'project_id'}))
        except sqlite3.Error as e:
            print(f"Database Error creating project: {e}")
            raise

    def list_projects(self, team_id: int | None = None) -> List[Project]:
        """Retrieves projects, optionally filtered by team."""
        query = "SELECT * FROM projects"
        params = []
        if team_id is not None:
            query += " WHERE team_id = ?"
            params.append(team_id)
        query += " ORDER BY start_date DESC" # Example ordering

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [Project(**dict(row)) for row in rows]

    def get_project_by_id(self, project_id: int) -> Project | None:
        """Retrieves a project by its ID."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM projects WHERE project_id = ?", (project_id,))
            row = cursor.fetchone()
            if row:
                return Project(**dict(row))
            return None

    # --- Team Member Methods (Many-to-Many) ---

    def create_team_member(self, team_member: TeamMember) -> TeamMember | None:
        """Adds a user to a team."""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO team_members (team_id, user_id, role_in_team) VALUES (?, ?, ?)",
                    (team_member.team_id, team_member.user_id, team_member.role_in_team),
                )
                conn.commit()
                team_member_id = cursor.lastrowid
                return TeamMember(team_member_id=team_member_id, **team_member.dict(exclude={'team_member_id'}))
        except sqlite3.IntegrityError:
            # User might already be in the team (UNIQUE constraint)
            print(f"Integrity Error: User {team_member.user_id} might already be in team {team_member.team_id}")
            return None # Indicate failure due to constraint
        except sqlite3.Error as e:
            print(f"Database Error adding team member: {e}")
            raise

    def list_team_members(self) -> List[TeamMember]:
        """Retrieves all team member relationships."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM team_members")
            rows = cursor.fetchall()
            return [TeamMember(**dict(row)) for row in rows]

    def get_team_member_by_id(self, team_member_id: int) -> TeamMember | None:
        """Retrieves a specific team member relationship entry by its ID."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM team_members WHERE team_member_id = ?", (team_member_id,))
            row = cursor.fetchone()
            if row:
                return TeamMember(**dict(row))
            return None

    def get_members_by_team_id(self, team_id: int) -> List[TeamMember]:
        """Retrieves all members for a specific team."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM team_members WHERE team_id = ?", (team_id,))
            rows = cursor.fetchall()
            return [TeamMember(**dict(row)) for row in rows]

    def get_teams_for_user_id(self, user_id: int) -> List[TeamMember]:
        """Retrieves all team memberships for a specific user."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM team_members WHERE user_id = ?", (user_id,))
            rows = cursor.fetchall()
            return [TeamMember(**dict(row)) for row in rows]

    # Add update/delete methods for teams, projects, team members if required
    # def remove_team_member(self, team_id: int, user_id: int): ...