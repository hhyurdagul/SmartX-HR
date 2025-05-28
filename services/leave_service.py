from models import LeaveRequest, LeaveBalance, User
from repositories.leave_repository import LeaveRepository
from repositories.user_repository import UserRepository
from fastapi import Depends, HTTPException
from typing import List, Dict, Optional # Added Optional
import asyncio # Added asyncio
# Removed: from .ai_service import AIService

class LeaveService:
    """Encapsulates business logic related to leave requests and balances."""

    def __init__(
        self,
        leave_repository: LeaveRepository = Depends(),
        user_repository: UserRepository = Depends()
        # Removed: ai_service: AIService = Depends()
    ):
        self.leave_repository = leave_repository
        self.user_repository = user_repository
        # Removed: self.ai_service = ai_service

    def _check_user_exists(self, user_id: int) -> User:
        """Helper to check if a user exists, raising HTTPException if not."""
        user = self.user_repository.get_user_by_id(user_id)
        if user is None:
            raise HTTPException(status_code=404, detail=f"User with ID {user_id} not found")
        return user

    async def create_leave_request(self, leave_request_data: LeaveRequest) -> LeaveRequest:
        """Creates a new leave request after validation."""
        self._check_user_exists(leave_request_data.user_id) # User existence check remains

        # AI-related logic removed:
        # - user_data_dict removed
        # - team_context_dict removed
        # - AI service call and response handling removed
        # - Setting of ai_* fields on leave_request_data removed

        # Ensure status is 'pending' on creation if not provided or invalid
        if leave_request_data.status != "pending":
             print(f"Warning: Forcing status to 'pending' for new leave request for user {leave_request_data.user_id}")
             leave_request_data.status = "pending"
        
        # Ensure AI fields are not inadvertently carried over if present in input
        leave_request_data.ai_priority_score = None
        leave_request_data.ai_suggested_priority = None
        leave_request_data.ai_reasoning = None
        leave_request_data.ai_error_message = None

        try:
            # This is a synchronous call; FastAPI handles it in a thread pool
            created_request = self.leave_repository.create_request(leave_request_data)
            # Maybe trigger a notification here?
            return created_request
        except Exception as e:
            print(f"Error creating leave request in service: {e}")
            raise HTTPException(status_code=500, detail="Failed to create leave request.")

    def get_leave_request(self, leave_request_id: int) -> LeaveRequest:
        """Retrieves a specific leave request."""
        request = self.leave_repository.get_request_by_id(leave_request_id)
        if request is None:
            raise HTTPException(status_code=404, detail=f"Leave request with ID {leave_request_id} not found")
        return request

    def list_leave_requests(self) -> List[LeaveRequest]:
        """Retrieves all leave requests."""
        # Could add filtering/pagination logic here later
        return self.leave_repository.list_requests()

    def update_leave_request_status(self, leave_request_id: int, status: str) -> LeaveRequest:
        """Updates the status of a leave request."""
        # Validate the status value
        allowed_statuses = ["approved", "rejected", "pending"] # Could be an Enum
        if status not in allowed_statuses:
            raise HTTPException(status_code=400, detail=f"Invalid status '{status}'. Must be one of {allowed_statuses}")

        # Check if the request exists first
        existing_request = self.get_leave_request(leave_request_id) # Reuse get method for 404 check

        # Add business logic for status transitions if needed
        # e.g., cannot approve an already rejected request without specific override logic

        try:
            updated_request = self.leave_repository.update_request_status(leave_request_id, status)
            if updated_request is None:
                 # This case might happen if the rowcount was 0 in repo, double-check logic
                 raise HTTPException(status_code=404, detail=f"Leave request with ID {leave_request_id} not found during update.")

            # If approved/rejected, potentially update LeaveBalance here
            # if status in ["approved", "rejected"]:
            #    self._update_leave_balance_after_request(existing_request.user_id, existing_request, status)

            # Maybe trigger notifications on status change?
            return updated_request
        except Exception as e:
            print(f"Error updating leave request status in service: {e}")
            raise HTTPException(status_code=500, detail="Failed to update leave request status.")


    def get_user_leave_balance(self, user_id: int) -> LeaveBalance:
        """Retrieves the leave balance for a user."""
        self._check_user_exists(user_id)
        balance = self.leave_repository.get_balance_by_user_id(user_id)
        if balance is None:
            # Decide if this is a 404 or if we should create/return a default balance
            raise HTTPException(status_code=404, detail=f"Leave balance for user ID {user_id} not found.")
        return balance

    # --- Potential private helper for balance updates ---
    # def _update_leave_balance_after_request(self, user_id: int, request: LeaveRequest, new_status: str):
    #     # Logic to calculate leave days used and update LeaveBalance record
    #     pass

    async def update_leave_request_ai_assessment(self, leave_request_id: int, ai_data: Dict) -> LeaveRequest:
        """Updates the AI assessment for a given leave request."""
        try:
            updated_request = await asyncio.to_thread(
                self.leave_repository.update_request_ai_assessment, 
                leave_request_id, 
                ai_data
            )
            if updated_request is None:
                raise HTTPException(
                    status_code=404, 
                    detail=f"Leave request with ID {leave_request_id} not found for AI update."
                )
            return updated_request
        except Exception as e:
            # Log the exception e
            print(f"Error during AI assessment update for request {leave_request_id}: {e}")
            # Re-raise a generic server error or a more specific one if applicable
            raise HTTPException(status_code=500, detail="Failed to update AI assessment for leave request.")

    async def update_leave_request_status_and_ai_reasoning(self, leave_request_id: int, new_status: str, ai_reasoning_text: Optional[str], ai_error_msg: Optional[str]) -> LeaveRequest:
        """Updates the status, AI reasoning, and AI error message of a specific leave request."""
        try:
            # Add validation for new_status if it's not covered elsewhere or if specific values are expected
            allowed_statuses = ["approved", "rejected", "pending", "needs discussion"] # Extend if needed
            if new_status not in allowed_statuses:
                raise HTTPException(status_code=400, detail=f"Invalid new_status '{new_status}'. Must be one of {allowed_statuses}")

            updated_request = await asyncio.to_thread(
                self.leave_repository.update_request_status_and_ai_reasoning, 
                leave_request_id, 
                new_status, 
                ai_reasoning_text, 
                ai_error_msg
            )
            if updated_request is None:
                raise HTTPException(
                    status_code=404, 
                    detail=f"Leave request with ID {leave_request_id} not found for status and AI reasoning update."
                )
            return updated_request
        except HTTPException: # Re-raise HTTPException directly (e.g., from status validation)
            raise
        except Exception as e:
            # Log the exception e
            print(f"Error updating status and AI reasoning for leave request {leave_request_id}: {e}")
            # Re-raise a generic server error
            raise HTTPException(status_code=500, detail="Failed to update leave request status and AI reasoning.")