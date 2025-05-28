from fastapi import APIRouter, Depends, HTTPException, Body
from models import KPI, KPICategory, KPIResult, User # Import User
from services.kpi_service import KpiService
from services.user_service import UserService # Added UserService
from services.ai_service import AIService # Added AIService
from auth import require_admin_role, require_authenticated_user # Import auth dependencies
from typing import List, Dict # Added Dict
from pydantic import BaseModel, conlist # Added Pydantic imports
import asyncio # Added asyncio

router = APIRouter(
    prefix="/kpi",    # Base prefix for KPI routes
    tags=["KPIs"]     # Tag for OpenAPI documentation
)

# Pydantic model for the request body
class AssessKpiResultsPayload(BaseModel):
    kpi_result_ids: conlist(int, min_length=1)
    user_id: int # User for whom these KPI results belong


# --- KPI Category Endpoints ---

@router.post("/categories", response_model=KPICategory, status_code=201)
async def create_kpi_category(
    category_data: KPICategory,
    kpi_service: KpiService = Depends(KpiService),
    admin_user: User = Depends(require_admin_role) # Require admin role
):
    """Creates a new KPI category. (Admin Only)"""
    return kpi_service.create_kpi_category(category_data)

@router.get("/categories", response_model=List[KPICategory])
async def list_kpi_categories(
    kpi_service: KpiService = Depends(KpiService),
    current_user: User = Depends(require_authenticated_user) # Require authentication
):
    """Retrieves all KPI categories. (Requires Authentication)"""
    return kpi_service.list_kpi_categories()

@router.get("/categories/{category_id}", response_model=KPICategory)
async def get_kpi_category(
    category_id: int,
    kpi_service: KpiService = Depends(KpiService),
    current_user: User = Depends(require_authenticated_user)
):
    """Retrieves a specific KPI category by its ID. (Requires Authentication)"""
    return kpi_service.get_kpi_category(category_id)


# --- KPI Endpoints ---

# Note: Changed prefix from "/kpis" to "/" relative to "/kpi" prefix
@router.post("/", response_model=KPI, status_code=201)
async def create_kpi(
    kpi_data: KPI,
    kpi_service: KpiService = Depends(KpiService),
    admin_user: User = Depends(require_admin_role) # Require admin role
):
    """Creates a new Key Performance Indicator (KPI). (Admin Only)"""
    # Service handles validation (e.g., category exists)
    return kpi_service.create_kpi(kpi_data)

@router.get("/", response_model=List[KPI])
async def list_kpis(kpi_service: KpiService = Depends(KpiService), current_user: User = Depends(require_authenticated_user)):
    """Retrieves all KPIs."""
    return kpi_service.list_kpis()

@router.get("/{kpi_id}", response_model=KPI)
async def get_kpi(
    kpi_id: int,
    kpi_service: KpiService = Depends(KpiService),
    current_user: User = Depends(require_authenticated_user)
):
    """Retrieves a specific KPI by its ID. (Requires Authentication)"""
    return kpi_service.get_kpi(kpi_id)


# --- KPI Result Endpoints ---

@router.post("/results", response_model=KPIResult, status_code=201)
async def create_kpi_result(
    result_data: KPIResult,
    kpi_service: KpiService = Depends(KpiService),
    admin_user: User = Depends(require_admin_role) # Require admin role (or adjust if needed)
):
    """Records a new KPI result for a user. (Admin Only - adjust if needed)"""
    # Service handles validation (user exists, kpi exists)
    return kpi_service.create_kpi_result(result_data)

@router.get("/results", response_model=List[KPIResult])
async def list_kpi_results(
    user_id: int | None = None, # Optional query parameter
    kpi_id: int | None = None,  # Optional query parameter
    kpi_service: KpiService = Depends(KpiService),
    current_user: User = Depends(require_authenticated_user)
):
    """
    Retrieves KPI results. Can be filtered by `user_id` and/or `kpi_id`
    using query parameters (e.g., `/kpi/results?user_id=1`).
    (Requires Authentication)
    """
    return kpi_service.list_kpi_results(user_id=user_id, kpi_id=kpi_id)

@router.get("/results/{result_id}", response_model=KPIResult)
async def get_kpi_result(
    result_id: int,
    kpi_service: KpiService = Depends(KpiService),
    current_user: User = Depends(require_authenticated_user)
):
    """Retrieves a specific KPI result by its ID. (Requires Authentication)"""
    return kpi_service.get_kpi_result(result_id)

@router.post("/assess-batch", response_model=Dict, tags=["KPIs", "AI Assessment"])
async def assess_kpi_results_batch_endpoint(
    payload: AssessKpiResultsPayload = Body(...), 
    ai_service: AIService = Depends(), 
    kpi_service: KpiService = Depends(), 
    user_service: UserService = Depends(),
    auth_user: User = Depends(require_admin_role) # Changed current_user to auth_user for clarity
):
    """
    On-demand AI-driven assessment for a batch of KPI results for a specific user. (Admin Only)

    This endpoint processes a list of KPI result IDs for a specified user.
    It fetches the details for each KPI result, including its definition (name, description).
    This data, along with user context, is then sent to an AI service to obtain a
    qualitative assessment (e.g., 'Exceeds Expectations', 'Meets Expectations') and
    reasoning for each KPI result. The AI's assessment and reasoning are then
    updated in the database for each respective KPI result.

    Request Body:
    - `kpi_result_ids`: A list of integers representing the IDs of the KPI results to be assessed.
    - `user_id`: The integer ID of the user to whom these KPI results belong.

    Returns:
    A dictionary summarizing the operation, including:
    - `message`: A general status message.
    - `ai_service_error`: Any general error message from the AI service itself (if applicable).
    - `successful_updates`: Count of KPI results successfully updated with AI assessment.
    - `update_failures`: A list of objects, each detailing a failure for a specific KPI result
      (e.g., AI processing error for that item, database update error).
    - `initial_fetch_errors`: A list of objects, each detailing an error encountered during
      the initial fetching of KPI result data (e.g., KPI result not found, not belonging to the user).
    """
    # 4. Data Fetching Logic
    user_details_model = await asyncio.to_thread(user_service.user_repository.get_user_by_id, payload.user_id)
    if not user_details_model:
        raise HTTPException(status_code=404, detail=f"User with ID {payload.user_id} not found.")
    user_details_dict = user_details_model.dict()

    kpi_results_for_ai = []
    fetch_errors = []
    processed_ids = set()

    for req_id in payload.kpi_result_ids:
        if req_id in processed_ids:
            fetch_errors.append({"id": req_id, "error": "Duplicate ID in request."})
            continue
        processed_ids.add(req_id)

        kpi_result = await asyncio.to_thread(kpi_service.kpi_repository.get_result_by_id, req_id)

        if not kpi_result:
            fetch_errors.append({"id": req_id, "error": "KPI Result not found."})
            continue
        
        if kpi_result.user_id != payload.user_id:
            fetch_errors.append({"id": req_id, "error": f"KPI Result belongs to user {kpi_result.user_id}, not requested user {payload.user_id}."})
            continue

        kpi_def = await asyncio.to_thread(kpi_service.kpi_repository.get_kpi_by_id, kpi_result.kpi_id)
        if not kpi_def:
            fetch_errors.append({"id": req_id, "error": f"KPI definition (ID: {kpi_result.kpi_id}) for KPI Result not found."})
            continue
        
        kpi_results_for_ai.append({
            'result_id': kpi_result.result_id,
            'kpi_id': kpi_result.kpi_id,
            'kpi_name': kpi_def.kpi_name,
            'kpi_description': kpi_def.description,
            'unit': kpi_def.unit,
            'period': kpi_result.period,
            'target': kpi_result.target,
            'actual_value': kpi_result.actual_value
        })

    # 5. Endpoint Logic - AI Processing & Update
    if not kpi_results_for_ai:
        if fetch_errors: # Only return fetch_errors if no valid items were found to process
            return {"message": "No valid KPI results to process.", "initial_fetch_errors": fetch_errors}
        # This case might occur if payload.kpi_result_ids was empty or all were duplicates handled by processed_ids
        return {"message": "No KPI results provided or all were duplicates."}


    ai_output = await ai_service.assess_kpi_results(kpi_results_for_ai, user_details_dict)
    
    successful_updates = 0
    update_failures = []

    for assessed_kpi_data in ai_output.get("assessed_kpis", []):
        result_id_from_ai = assessed_kpi_data.get('result_id')
        if result_id_from_ai is None: # Should not happen if AIService behaves
            print(f"AI assessment data missing 'result_id': {assessed_kpi_data}")
            update_failures.append({"id": "Unknown", "error": "AI assessment data format error (missing result_id)."})
            continue

        # Check if AI itself reported an error for this item during its processing
        if assessed_kpi_data.get("ai_error_message"): # Field used by AIService for item-specific AI errors
            update_failures.append({"id": result_id_from_ai, "error": f"AI assessment error: {assessed_kpi_data['ai_error_message']}"})
            continue
        
        # Check if the AI assessment fields are just placeholder errors from AI service if parsing failed for that item
        if assessed_kpi_data.get("ai_assessment", "").startswith("Error:") :
             update_failures.append({"id": result_id_from_ai, "error": f"AI assessment content error: {assessed_kpi_data.get('ai_assessment')} - Reasoning: {assessed_kpi_data.get('ai_reasoning')}"})
             continue


        try:
            await kpi_service.update_kpi_result_ai_assessment(result_id_from_ai, assessed_kpi_data)
            successful_updates += 1
        except HTTPException as e:
            update_failures.append({"id": result_id_from_ai, "error": f"DB update failed: {e.detail}"})
        except Exception as e:
            update_failures.append({"id": result_id_from_ai, "error": f"DB update failed (unexpected): {str(e)}"})

    return {
        "message": "KPI assessment processed.",
        "ai_service_error": ai_output.get("error_message"), # General error from AI service, if any
        "successful_updates": successful_updates,
        "update_failures": update_failures,
        "initial_fetch_errors": fetch_errors
    }