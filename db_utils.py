import sqlite3
# Models are no longer directly used here for CRUD, but might be needed if
# initialize_database adds default data later. Keep for now or remove if unused.
# from models import User, LeaveRequest, LeaveBalance, KPI, KPICategory, KPIResult, TrainingCategory, TrainingCourse, UserTrainingProgress, Team, Project, TeamMember

DATABASE_NAME = "smartx_db.db"

def get_db_connection():
    """Gets a database connection (used primarily for initialization)."""
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row # To access columns by name
    return conn

def initialize_database():
    """Creates all database tables if they don't exist."""
    print("Initializing database schema...")
    conn = get_db_connection()
    cursor = conn.cursor()

    # Users Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            role TEXT NOT NULL,
            start_date TEXT,
            password TEXT NOT NULL -- Storing plain text password (INSECURE!)
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

    # Training Courses Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS training_courses (
            training_course_id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_name TEXT NOT NULL,
            description TEXT,
            duration_hours INTEGER
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
    print("Database schema initialized.")

# All specific CRUD functions (_db) have been removed and migrated to repository classes.