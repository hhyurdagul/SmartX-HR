from models import LeaveRequest, LeaveBalance
from .base_repository import get_db_connection
from typing import List
import sqlite3

class LeaveRepository:
    """Handles database operations for LeaveRequest and LeaveBalance entities."""

    def create_request(self, leave_request: LeaveRequest) -> LeaveRequest:
        """Creates a new leave request in the database."""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO leave_requests (user_id, leave_type, start_date, end_date, reason, status, ai_reasoning, ai_error_message) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        leave_request.user_id, 
                        leave_request.leave_type, 
                        leave_request.start_date, 
                        leave_request.end_date, 
                        leave_request.reason, 
                        leave_request.status,
                        leave_request.ai_reasoning, # Will be None on initial creation
                        leave_request.ai_error_message # Will be None on initial creation
                    ),
                )
                conn.commit()
                leave_request_id = cursor.lastrowid
                # Return the request with the generated ID
                return LeaveRequest(leave_request_id=leave_request_id, **leave_request.dict(exclude={'leave_request_id'}))
        except sqlite3.Error as e:
            print(f"Database Error creating leave request: {e}")
            raise # Re-raise for service layer handling

    def list_requests(self) -> List[LeaveRequest]:
        """Retrieves all leave requests."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM leave_requests ORDER BY start_date DESC") # Example ordering
            rows = cursor.fetchall()
            return [LeaveRequest(**dict(row)) for row in rows]

    def get_request_by_id(self, leave_request_id: int) -> LeaveRequest | None:
        """Retrieves a specific leave request by its ID."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM leave_requests WHERE leave_request_id = ?", (leave_request_id,))
            row = cursor.fetchone()
            if row:
                return LeaveRequest(**dict(row))
            return None

    def update_request_status(self, leave_request_id: int, status: str) -> LeaveRequest | None:
        """Updates the status of a specific leave request."""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE leave_requests SET status = ? WHERE leave_request_id = ?", (status, leave_request_id))
                conn.commit()
                if cursor.rowcount == 0: # Check if any row was updated
                    return None # Indicate request not found or status unchanged
            # Return the updated request data
            return self.get_request_by_id(leave_request_id)
        except sqlite3.Error as e:
            print(f"Database Error updating leave request status: {e}")
            raise

    def update_request_status_and_ai_reasoning(self, leave_request_id: int, new_status: str, ai_reasoning_text: Optional[str], ai_error_msg: Optional[str]) -> Optional[LeaveRequest]:
        """Updates the status, AI reasoning, and AI error message of a specific leave request."""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    UPDATE leave_requests 
                    SET status = ?, 
                        ai_reasoning = ?, 
                        ai_error_message = ?
                    WHERE leave_request_id = ?
                    """,
                    (new_status, ai_reasoning_text, ai_error_msg, leave_request_id)
                )
                conn.commit()
                if cursor.rowcount == 0:
                    return None # Indicate request not found or no change needed
            # Return the updated request data
            return self.get_request_by_id(leave_request_id)
        except sqlite3.Error as e:
            print(f"Database Error updating leave request status and AI reasoning: {e}")
            raise

    # --- Leave Balance Methods ---

    def get_balance_by_user_id(self, user_id: int) -> LeaveBalance | None:
        """Retrieves the leave balance for a specific user."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM leave_balances WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            if row:
                return LeaveBalance(**dict(row))
            return None

    # Add create/update balance methods if needed, e.g., when a user is created or leave is taken/adjusted.
    # def update_balance(self, user_id: int, used_days_delta: int): ...
    # def create_initial_balance(self, user_id: int, total_days: int): ...
