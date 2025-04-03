from models import User, UserCreate # Import UserCreate
from .base_repository import get_db_connection
import sqlite3 # Needed for IntegrityError

class UserRepository:
    """Handles database operations for the User entity."""

    def create_user(self, user_data: UserCreate) -> User:
        """Creates a new user in the database, including the plain text password."""
        # WARNING: Storing plain text passwords is highly insecure!
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO users (username, email, role, start_date, password) VALUES (?, ?, ?, ?, ?)",
                    (user_data.username, user_data.email, user_data.role, user_data.start_date, user_data.password),
                )
                conn.commit()
                user_id = cursor.lastrowid
                # Return the user data *without* the password
                user_dict = user_data.dict(exclude={'password', 'user_id'}) # Exclude password from response
                return User(user_id=user_id, **user_dict)
        except sqlite3.IntegrityError as e:
            # Handle potential unique constraint violations (e.g., email or username if unique)
            print(f"Database Error creating user: {e}") # Basic logging
            raise # Re-raise for now, service layer can handle

    def get_user_by_id(self, user_id: int) -> User | None:
        """Retrieves a user by their ID."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            if row:
                # Return User model including the password for authentication checks
                return User(**dict(row))
            return None

    def get_user_by_username_or_email(self, username_or_email: str) -> User | None:
        """Retrieves a user by their username or email."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ? OR email = ?", (username_or_email, username_or_email))
            row = cursor.fetchone()
            if row:
                # Return User model including the password for authentication checks
                return User(**dict(row))
            return None

    # Add other user-related methods here if needed (e.g., list_all, update, delete)