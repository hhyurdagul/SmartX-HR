from fastapi import APIRouter, Depends, HTTPException, Body
from models import LeaveRequest, LeaveBalance, User # User might be needed for context
from services.leave_service import LeaveService
from services.user_service import UserService
from services.ai_service import AIService # Added AIService import
from services.team_service import TeamService # Added TeamService import
from auth import require_admin_role, require_authenticated_user # Import auth dependencies
from typing import List, Dict # Added Dict
from pydantic import BaseModel, conlist # Added Pydantic imports
import asyncio # Added asyncio
from collections import defaultdict # Added defaultdict import

router = APIRouter(
    prefix="/leaves", # Base prefix for leave-related routes
    tags=["Leaves"]    # Tag for OpenAPI documentation
)

# Pydantic model for the request body
class PrioritizeBatchPayload(BaseModel):
    leave_request_ids: conlist(int, min_length=1)


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
    return await leave_service.create_leave_request(leave_request_data)

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

@router.post("/prioritize-batch", response_model=Dict)
async def prioritize_leave_requests_batch_endpoint( # Renamed for clarity from previous generic name
    payload: PrioritizeBatchPayload = Body(...), 
    ai_service: AIService = Depends(), 
    leave_service: LeaveService = Depends(), 
    user_service: UserService = Depends(), # Kept for potential future use, though not directly used for user details now
    team_service: TeamService = Depends(), # Added TeamService
    admin_user: User = Depends(require_admin_role)
):
    """
    On-demand AI-driven status decision for a batch of leave requests. (Admin Only)

    This endpoint processes a list of leave request IDs. It groups these requests
    by their respective teams (based on the user who submitted the request).
    For each team, it calls an AI service to suggest a status (approved, rejected,
    needs discussion) and provide reasoning for each leave request within that team.
    The leave request's status and the AI's reasoning are then updated in the database.

    Request Body:
    - `leave_request_ids`: A list of integers representing the IDs of the leave requests to be processed.

    Returns:
    A dictionary summarizing the operation, including the count of successful updates,
    details of any failures during the update process (e.g., AI errors, database errors),
    and any errors encountered during the initial data fetching phase.
    """
    fetch_errors: List[Dict] = []
    team_grouped_requests: Dict[int, List[Dict]] = defaultdict(list)
    valid_leave_requests_map: Dict[int, LeaveRequest] = {}
    processed_ids_for_fetching = set()

    # Initial Data Fetch & Validation (Leave Requests)
    for req_id in payload.leave_request_ids:
        if req_id in processed_ids_for_fetching:
            print(f"Skipping duplicate leave_request_id in payload: {req_id}")
            fetch_errors.append({'id': req_id, 'error': 'Duplicate ID in request payload.'})
            continue
        processed_ids_for_fetching.add(req_id)

        try:
            leave_request = await asyncio.to_thread(leave_service.leave_repository.get_request_by_id, req_id)
            if not leave_request:
                fetch_errors.append({'id': req_id, 'error': f'Leave request with ID {req_id} not found.'})
                continue
            valid_leave_requests_map[req_id] = leave_request
        except Exception as e:
            fetch_errors.append({'id': req_id, 'error': f'Error fetching leave request ID {req_id}: {str(e)}'})

    # Grouping by Team ID
    for req_id, leave_request in valid_leave_requests_map.items():
        user_id = leave_request.user_id
        try:
            team_id = await team_service.get_team_id_for_user_async(user_id)
            if team_id is None:
                fetch_errors.append({'id': req_id, 'error': f'User {user_id} (for leave request {req_id}) not assigned to any team.'})
                continue
            
            team_grouped_requests[team_id].append({
                'id': leave_request.leave_request_id, 
                'reason': leave_request.reason
                # Add other fields if your AI service's decide_leave_request_statuses_for_team expects more
            })
        except Exception as e:
            fetch_errors.append({'id': req_id, 'error': f'Error fetching team for user {user_id} (leave request {req_id}): {str(e)}'})


    # AI Processing & DB Update
    update_success_count = 0
    update_failure_details: List[Dict] = []

    if not team_grouped_requests and fetch_errors:
        return {
            "message": "Leave request prioritization processed. No requests were valid for AI processing.", 
            "successful_updates": 0, 
            "update_failures": [], 
            "initial_fetch_errors": fetch_errors
        }
    if not team_grouped_requests:
         return {
            "message": "No leave requests to process after filtering (e.g., all users without teams or no valid IDs).",
            "successful_updates": 0, 
            "update_failures": [], 
            "initial_fetch_errors": fetch_errors
        }


    for team_id, requests_for_team in team_grouped_requests.items():
        if not requests_for_team:
            continue # Should not happen due to defaultdict logic but good practice

        try:
            team_ai_outcomes = await ai_service.decide_leave_request_statuses_for_team(
                requests_for_team, 
                team_id_for_context=str(team_id)
            )

            for ai_outcome in team_ai_outcomes:
                current_req_id = ai_outcome.get('id')
                if current_req_id is None: # Should not happen if AI service is correct
                    update_failure_details.append({'id': 'Unknown', 'error': 'AI outcome missing request ID.'})
                    continue

                if ai_outcome.get('ai_error_message'):
                    update_failure_details.append({
                        'id': current_req_id, 
                        'error': f"AI processing error: {ai_outcome['ai_error_message']}"
                    })
                else:
                    try:
                        await leave_service.update_leave_request_status_and_ai_reasoning(
                            current_req_id, 
                            ai_outcome['status'], 
                            ai_outcome.get('ai_reasoning'), 
                            None # Explicitly pass None for ai_error_message if AI succeeded
                        )
                        update_success_count += 1
                    except HTTPException as e_http:
                        update_failure_details.append({'id': current_req_id, 'error': f"DB update failed: {e_http.detail}"})
                    except Exception as e_db:
                        update_failure_details.append({'id': current_req_id, 'error': f"DB update failed (unexpected): {str(e_db)}"})
        except Exception as e_ai_service:
            # This catches errors from the call to decide_leave_request_statuses_for_team itself
            for req_in_failed_batch in requests_for_team:
                 update_failure_details.append({'id': req_in_failed_batch['id'], 'error': f"AI service call failed for team {team_id}: {str(e_ai_service)}"})


    return {
        "message": "Leave request prioritization processed.", 
        "successful_updates": update_success_count, 
        "update_failures": update_failure_details, 
        "initial_fetch_errors": fetch_errors
    }