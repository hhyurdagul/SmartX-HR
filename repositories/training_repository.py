from models import TrainingCourse, UserTrainingProgress
from .base_repository import get_db_connection
from typing import List, Dict, Any
import sqlite3

class TrainingRepository:
    """Handles database operations for TrainingCourse, and UserTrainingProgress."""
    # --- Training Course Methods ---

    def create_course(self, course: TrainingCourse) -> TrainingCourse:
        """Creates a new training course."""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO training_courses (course_name, description, duration_hours) VALUES (?, ?, ?, ?)",
                    (course.course_name, course.description, course.duration_hours),
                )
                conn.commit()
                course_id = cursor.lastrowid
                return TrainingCourse(training_course_id=course_id, **course.dict(exclude={'training_course_id'}))
        except sqlite3.Error as e:
            print(f"Database Error creating training course: {e}")
            raise

    def list_courses(self) -> List[TrainingCourse]:
        """Retrieves training courses, optionally filtered by category."""
        query = "SELECT * FROM training_courses"
        params = []
        query += " ORDER BY course_name"

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [TrainingCourse(**dict(row)) for row in rows]

    def get_course_by_id(self, course_id: int) -> TrainingCourse | None:
        """Retrieves a training course by its ID."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM training_courses WHERE training_course_id = ?", (course_id,))
            row = cursor.fetchone()
            if row:
                return TrainingCourse(**dict(row))
            return None

    # --- User Training Progress Methods ---

    def create_progress(self, progress: UserTrainingProgress) -> UserTrainingProgress:
        """Creates a new user training progress record."""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO user_training_progress (user_id, training_course_id, enrollment_date, completion_percentage, is_completed) VALUES (?, ?, ?, ?, ?)",
                    (progress.user_id, progress.training_course_id, progress.enrollment_date, progress.completion_percentage, progress.is_completed),
                )
                conn.commit()
                progress_id = cursor.lastrowid
                return UserTrainingProgress(progress_id=progress_id, **progress.dict(exclude={'progress_id'}))
        except sqlite3.Error as e:
            print(f"Database Error creating user training progress: {e}")
            raise

    def list_progress(self, user_id: int | None = None, course_id: int | None = None) -> List[UserTrainingProgress]:
        """Retrieves user training progress, optionally filtered by user or course."""
        query = "SELECT * FROM user_training_progress"
        params = []
        conditions = []
        if user_id is not None:
            conditions.append("user_id = ?")
            params.append(user_id)
        if course_id is not None:
            conditions.append("training_course_id = ?")
            params.append(course_id)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        query += " ORDER BY enrollment_date DESC" # Example ordering

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [UserTrainingProgress(**dict(row)) for row in rows]

    def get_progress_by_id(self, progress_id: int) -> UserTrainingProgress | None:
        """Retrieves a user training progress record by its ID."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM user_training_progress WHERE progress_id = ?", (progress_id,))
            row = cursor.fetchone()
            if row:
                return UserTrainingProgress(**dict(row))
            return None

    def update_progress(self, progress_id: int, progress_data: Dict[str, Any]) -> UserTrainingProgress | None:
        """Updates a user training progress record."""
        if not progress_data:
            # Or raise ValueError("No update data provided")
            return self.get_progress_by_id(progress_id)

        set_clause = ", ".join([f"{key} = ?" for key in progress_data.keys()])
        values = list(progress_data.values())
        values.append(progress_id)

        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(f"UPDATE user_training_progress SET {set_clause} WHERE progress_id = ?", values)
                conn.commit()
                if cursor.rowcount == 0:
                    return None # Progress record not found
            return self.get_progress_by_id(progress_id) # Return updated record
        except sqlite3.Error as e:
            print(f"Database Error updating user training progress: {e}")
            raise

    # Add delete methods if required