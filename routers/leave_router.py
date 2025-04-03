from fastapi import APIRouter, Depends, HTTPException, Body
from models import LeaveRequest, LeaveBalance, User # User might be needed for context
from services.leave_service import LeaveService
from services.user_service import UserService # To get current user context if needed
from auth import require_admin_role, require_authenticated_user # Import auth dependencies
from typing import List

router = APIRouter(
    prefix="/leaves", # Base prefix for leave-related routes
    tags=["Leaves"]    # Tag for OpenAPI documentation
)

# Removed get_current_user_simulated as it's replaced by require_authenticated_user


# --- Leave Request Endpoints ---

@router.post("/requests", response_model=LeaveRequest, status_code=201)
async def create_leave_request(
    leave_request_data: LeaveRequest,
    leave_service: LeaveService = Depends(LeaveService)
):
    """
    Submits a new leave request.
    """
    # Service handles validation, creation, and potential errors (like user not found)
    return leave_service.create_leave_request(leave_request_data)

@router.get("/requests", response_model=List[LeaveRequest])
async def list_leave_requests(
    leave_service: LeaveService = Depends(LeaveService),
    current_user: User = Depends(require_authenticated_user) # Require authentication
):
    """
    Retrieves a list of all leave requests. (Requires Authentication)
    """
    return leave_service.list_leave_requests()

@router.get("/requests/{leave_request_id}", response_model=LeaveRequest)
async def get_leave_request(
    leave_request_id: int,
    leave_service: LeaveService = Depends(LeaveService),
    current_user: User = Depends(require_authenticated_user) # Require authentication
):
    """
    Retrieves details of a specific leave request by its ID. (Requires Authentication)
    """
    # Service handles fetching and 404 if not found
    return leave_service.get_leave_request(leave_request_id)

@router.put("/requests/{leave_request_id}/status", response_model=LeaveRequest)
async def update_leave_request_status(
    leave_request_id: int,
    status_update: dict = Body(..., example={"status": "approved"}), # Expect {"status": "new_status"}
    leave_service: LeaveService = Depends(LeaveService),
    admin_user: User = Depends(require_admin_role) # Require admin role
):
    """
    Updates the status of a leave request (e.g., approve, reject). (Admin Only)
    Expects a JSON body like: `{"status": "approved"}`
    """
    new_status = status_update.get("status")
    if not new_status:
        raise HTTPException(status_code=400, detail="Missing 'status' in request body.")

    # Service handles validation, update, and errors
    return leave_service.update_leave_request_status(leave_request_id, new_status)


# --- Leave Balance Endpoints ---

@router.get("/balance/me", response_model=LeaveBalance)
async def get_my_leave_balance(
    # Replace simulated user getter with the standard auth dependency
    current_user: User = Depends(require_authenticated_user), # Require authentication
    leave_service: LeaveService = Depends(LeaveService)
):
    """
    Retrieves the leave balance for the currently authenticated user. (Requires Authentication)
    """
    # Service handles fetching balance and 404 errors
    return leave_service.get_user_leave_balance(current_user.user_id)

# Potential endpoint to get balance for a specific user (requires permissions check)
# @router.get("/balance/{user_id}", response_model=LeaveBalance)
# async def get_user_leave_balance(
#     user_id: int,
#     leave_service: LeaveService = Depends(LeaveService),
#     # Add dependency for permission check here
# ):
#     """ Gets leave balance for a specific user (requires appropriate permissions). """
#     # Add permission check logic here
#     return leave_service.get_user_leave_balance(user_id)