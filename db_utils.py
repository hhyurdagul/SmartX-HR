import sqlite3
from models import User, LeaveRequest, LeaveBalance, KPI, KPICategory, KPIResult, TrainingCategory, TrainingCourse, UserTrainingProgress, Team, Project, TeamMember # Import models

DATABASE_NAME = "smartx_db.db"

def get_db_connection():
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row # To access columns by name
    return conn

def initialize_database():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Users Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            role TEXT NOT NULL,
            start_date TEXT
        )
    """)

    # Leave Requests Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leave_requests (
            leave_request_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            leave_type TEXT NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            reason TEXT,
            status TEXT DEFAULT 'pending',
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    """)

    # Leave Balances Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leave_balances (
            leave_balance_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE,
            total_days INTEGER NOT NULL,
            used_days INTEGER NOT NULL,
            remaining_days INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    """)

    # KPI Category Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS kpi_categories (
            category_id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_name TEXT NOT NULL
        )
    """)

    # KPIs Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS kpis (
            kpi_id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_id INTEGER,
            kpi_name TEXT NOT NULL,
            unit TEXT,
            description TEXT,
            FOREIGN KEY (category_id) REFERENCES kpi_categories(category_id)
        )
    """)

    # KPI Results Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS kpi_results (
            result_id INTEGER PRIMARY KEY AUTOINCREMENT,
            kpi_id INTEGER,
            user_id INTEGER,
            period TEXT,
            target INTEGER,
            actual_value INTEGER,
            FOREIGN KEY (kpi_id) REFERENCES kpis(kpi_id),
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    """)

    # Training Category Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS training_categories (
            training_category_id INTEGER PRIMARY KEY AUTOINCREMENT,
            training_category_name TEXT NOT NULL
        )
    """)

    # Training Courses Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS training_courses (
            training_course_id INTEGER PRIMARY KEY AUTOINCREMENT,
            training_category_id INTEGER,
            course_name TEXT NOT NULL,
            description TEXT,
            duration_hours INTEGER,
            FOREIGN KEY (training_category_id) REFERENCES training_categories(training_category_id)
        )
    """)

    # User Training Progress Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_training_progress (
            progress_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            training_course_id INTEGER,
            enrollment_date TEXT NOT NULL,
            completion_percentage REAL DEFAULT 0.0,
            is_completed BOOLEAN DEFAULT FALSE,
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            FOREIGN KEY (training_course_id) REFERENCES training_courses(training_course_id)
        )
    """)

    # Teams Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS teams (
            team_id INTEGER PRIMARY KEY AUTOINCREMENT,
            team_name TEXT NOT NULL,
            description TEXT,
            team_lead_user_id INTEGER,
            FOREIGN KEY (team_lead_user_id) REFERENCES users(user_id)
        )
    """)

    # Projects Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            project_id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_name TEXT NOT NULL,
            description TEXT,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            team_id INTEGER,
            status TEXT DEFAULT 'planning',
            FOREIGN KEY (team_id) REFERENCES teams(team_id)
        )
    """)

    # Team Members Table (Many-to-Many relationship between Users and Teams)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS team_members (
            team_member_id INTEGER PRIMARY KEY AUTOINCREMENT,
            team_id INTEGER,
            user_id INTEGER,
            role_in_team TEXT,
            FOREIGN KEY (team_id) REFERENCES teams(team_id),
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            UNIQUE(team_id, user_id)
        )
    """)

    conn.commit()
    conn.close()


# User CRUD operations (Example - expand for others as needed)
def create_user_db(user: User):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (username, email, role, start_date) VALUES (?, ?, ?, ?)",
        (user.username, user.email, user.role, user.start_date),
    )
    conn.commit()
    user_id = cursor.lastrowid
    conn.close()
    return User(user_id=user_id, **user.dict())

def get_user_by_id_db(user_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return User(**dict(row))
    return None

# Leave Request CRUD operations (Example - expand for others as needed)
def create_leave_request_db(leave_request: LeaveRequest):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO leave_requests (user_id, leave_type, start_date, end_date, reason) VALUES (?, ?, ?, ?, ?)",
        (leave_request.user_id, leave_request.leave_type, leave_request.start_date, leave_request.end_date, leave_request.reason),
    )
    conn.commit()
    leave_request_id = cursor.lastrowid
    conn.close()
    return LeaveRequest(leave_request_id=leave_request_id, **leave_request.dict())

def list_leave_requests_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM leave_requests")
    rows = cursor.fetchall()
    conn.close()
    return [LeaveRequest(**dict(row)) for row in rows]

def get_leave_request_db(leave_request_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM leave_requests WHERE leave_request_id = ?", (leave_request_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return LeaveRequest(**dict(row))
    return None

def update_leave_request_status_db(leave_request_id: int, status: str): # Specific update function
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE leave_requests SET status = ? WHERE leave_request_id = ?", (status, leave_request_id))
    conn.commit()
    conn.close()
    return get_leave_request_db(leave_request_id) # Return updated request

# Leave Balance CRUD operations (Example - expand for others as needed)
def get_leave_balance_by_user_id_db(user_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM leave_balances WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return LeaveBalance(**dict(row))
    return None

# KPI Category CRUD operations
def create_kpi_category_db(category: KPICategory):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO kpi_categories (category_name) VALUES (?)", (category.category_name,))
    conn.commit()
    category_id = cursor.lastrowid
    conn.close()
    return KPICategory(category_id=category_id, category_name=category.category_name)

def list_kpi_categories_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM kpi_categories")
    rows = cursor.fetchall()
    conn.close()
    return [KPICategory(**dict(row)) for row in rows]

def get_kpi_category_db(category_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM kpi_categories WHERE category_id = ?", (category_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return KPICategory(**dict(row))
    return None

# KPI CRUD operations
def create_kpi_db(kpi: KPI):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO kpis (category_id, kpi_name, unit, description) VALUES (?, ?, ?, ?)",
        (kpi.category_id, kpi.kpi_name, kpi.unit, kpi.description),
    )
    conn.commit()
    kpi_id = cursor.lastrowid
    conn.close()
    return KPI(kpi_id=kpi_id, **kpi.dict())

def list_kpis_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM kpis")
    rows = cursor.fetchall()
    conn.close()
    return [KPI(**dict(row)) for row in rows]

def get_kpi_db(kpi_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM kpis WHERE kpi_id = ?", (kpi_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return KPI(**dict(row))
    return None

# KPI Result CRUD operations
def create_kpi_result_db(result: KPIResult):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO kpi_results (kpi_id, user_id, period, target, actual_value) VALUES (?, ?, ?, ?, ?)",
        (result.kpi_id, result.user_id, result.period, result.target, result.actual_value),
    )
    conn.commit()
    result_id = cursor.lastrowid
    conn.close()
    return KPIResult(result_id=result_id, **result.dict())

def list_kpi_results_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM kpi_results")
    rows = cursor.fetchall()
    conn.close()
    return [KPIResult(**dict(row)) for row in rows]

def get_kpi_result_db(result_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM kpi_results WHERE result_id = ?", (result_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return KPIResult(**dict(row))
    return None


# Training Category CRUD operations
def create_training_category_db(category: TrainingCategory):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO training_categories (training_category_name) VALUES (?)", (category.training_category_name,))
    conn.commit()
    category_id = cursor.lastrowid
    conn.close()
    return TrainingCategory(training_category_id=category_id, training_category_name=category.training_category_name)

def list_training_categories_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM training_categories")
    rows = cursor.fetchall()
    conn.close()
    return [TrainingCategory(**dict(row)) for row in rows]

def get_training_category_db(category_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM training_categories WHERE training_category_id = ?", (category_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return TrainingCategory(**dict(row))
    return None

# Training Course CRUD operations
def create_training_course_db(course: TrainingCourse):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO training_courses (training_category_id, course_name, description, duration_hours) VALUES (?, ?, ?, ?)",
        (course.training_category_id, course.course_name, course.description, course.duration_hours),
    )
    conn.commit()
    course_id = cursor.lastrowid
    conn.close()
    return TrainingCourse(training_course_id=course_id, **course.dict())

def list_training_courses_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM training_courses")
    rows = cursor.fetchall()
    conn.close()
    return [TrainingCourse(**dict(row)) for row in rows]

def get_training_course_db(course_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM training_courses WHERE training_course_id = ?", (course_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return TrainingCourse(**dict(row))
    return None

# User Training Progress CRUD operations
def create_user_training_progress_db(progress: UserTrainingProgress):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO user_training_progress (user_id, training_course_id, enrollment_date, completion_percentage, is_completed) VALUES (?, ?, ?, ?, ?)",
        (progress.user_id, progress.training_course_id, progress.enrollment_date, progress.completion_percentage, progress.is_completed),
    )
    conn.commit()
    progress_id = cursor.lastrowid
    conn.close()
    return UserTrainingProgress(progress_id=progress_id, **progress.dict())

def list_user_training_progress_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user_training_progress")
    rows = cursor.fetchall()
    conn.close()
    return [UserTrainingProgress(**dict(row)) for row in rows]

def get_user_training_progress_db(progress_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user_training_progress WHERE progress_id = ?", (progress_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return UserTrainingProgress(**dict(row))
    return None

def update_user_training_progress_db(progress_id: int, progress_data: dict): # Generic Update
    conn = get_db_connection()
    cursor = conn.cursor()
    set_clause = ", ".join([f"{key} = ?" for key in progress_data.keys()])
    values = list(progress_data.values())
    values.append(progress_id)
    cursor.execute(f"UPDATE user_training_progress SET {set_clause} WHERE progress_id = ?", values)
    conn.commit()
    conn.close()
    return get_user_training_progress_db(progress_id)


# --- Team CRUD operations ---
def create_team_db(team: Team):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO teams (team_name, description, team_lead_user_id) VALUES (?, ?, ?)",
        (team.team_name, team.description, team.team_lead_user_id),
    )
    conn.commit()
    team_id = cursor.lastrowid
    conn.close()
    return Team(team_id=team_id, **team.dict())

def list_teams_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM teams")
    rows = cursor.fetchall()
    conn.close()
    return [Team(**dict(row)) for row in rows]

def get_team_db(team_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM teams WHERE team_id = ?", (team_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return Team(**dict(row))
    return None

# --- Project CRUD operations ---
def create_project_db(project: Project):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO projects (project_name, description, start_date, end_date, team_id, status) VALUES (?, ?, ?, ?, ?, ?)",
        (project.project_name, project.description, project.start_date, project.end_date, project.team_id, project.status),
    )
    conn.commit()
    project_id = cursor.lastrowid
    conn.close()
    return Project(project_id=project_id, **project.dict())

def list_projects_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM projects")
    rows = cursor.fetchall()
    conn.close()
    return [Project(**dict(row)) for row in rows]

def get_project_db(project_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM projects WHERE project_id = ?", (project_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return Project(**dict(row))
    return None

# --- Team Member CRUD operations ---
def create_team_member_db(team_member: TeamMember):
    conn = get_db_connection()
    cursor = conn.cursor()
    try: # Handle potential UNIQUE constraint violation
        cursor.execute(
            "INSERT INTO team_members (team_id, user_id, role_in_team) VALUES (?, ?, ?)",
            (team_member.team_id, team_member.user_id, team_member.role_in_team),
        )
        conn.commit()
        team_member_id = cursor.lastrowid
        conn.close()
        return TeamMember(team_member_id=team_member_id, **team_member.dict())
    except sqlite3.IntegrityError:
        conn.close()
        return None # Or raise an exception, depending on your error handling strategy

def list_team_members_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM team_members")
    rows = cursor.fetchall()
    conn.close()
    return [TeamMember(**dict(row)) for row in rows]

def get_team_member_db(team_member_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM team_members WHERE team_member_id = ?", (team_member_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return TeamMember(**dict(row))
    return None

def get_team_members_by_team_id_db(team_id: int): # Get members of a specific team
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM team_members WHERE team_id = ?", (team_id,))
    rows = cursor.fetchall()
    conn.close()
    return [TeamMember(**dict(row)) for row in rows]

def get_teams_for_user_db(user_id: int): # Get teams a user belongs to
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM team_members WHERE user_id = ?", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return [TeamMember(**dict(row)) for row in rows] 