from fastapi import APIRouter, Depends, HTTPException
from models import KPI, KPICategory, KPIResult, User # Import User
from services.kpi_service import KpiService
from auth import require_admin_role, require_authenticated_user # Import auth dependencies
from typing import List

router = APIRouter(
    prefix="/kpi",    # Base prefix for KPI routes
    tags=["KPIs"]     # Tag for OpenAPI documentation
)

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
    return kpi_service.get_kpi_result(result_id)