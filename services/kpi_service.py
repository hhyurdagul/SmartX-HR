from models import KPI, KPICategory, KPIResult, User
from repositories.kpi_repository import KpiRepository
from repositories.user_repository import UserRepository # To validate user IDs
from fastapi import Depends, HTTPException
from typing import List

class KpiService:
    """Encapsulates business logic related to KPIs, Categories, and Results."""

    def __init__(
        self,
        kpi_repository: KpiRepository = Depends(),
        user_repository: UserRepository = Depends()
    ):
        self.kpi_repository = kpi_repository
        self.user_repository = user_repository

    def _check_user_exists(self, user_id: int):
        """Helper to check if a user exists."""
        user = self.user_repository.get_user_by_id(user_id)
        if user is None:
            raise HTTPException(status_code=404, detail=f"User with ID {user_id} not found")
        return user

    def _check_kpi_exists(self, kpi_id: int):
        """Helper to check if a KPI exists."""
        kpi = self.kpi_repository.get_kpi_by_id(kpi_id)
        if kpi is None:
            raise HTTPException(status_code=404, detail=f"KPI with ID {kpi_id} not found")
        return kpi

    def _check_category_exists(self, category_id: int):
        """Helper to check if a KPI Category exists."""
        category = self.kpi_repository.get_category_by_id(category_id)
        if category is None:
            raise HTTPException(status_code=404, detail=f"KPI Category with ID {category_id} not found")
        return category

    # --- KPI Category Methods ---

    def create_kpi_category(self, category_data: KPICategory) -> KPICategory:
        """Creates a new KPI category."""
        # Add validation if needed (e.g., check for duplicate names?)
        try:
            return self.kpi_repository.create_category(category_data)
        except Exception as e:
            print(f"Error creating KPI category in service: {e}")
            raise HTTPException(status_code=500, detail="Failed to create KPI category.")

    def get_kpi_category(self, category_id: int) -> KPICategory:
        """Retrieves a specific KPI category."""
        category = self.kpi_repository.get_category_by_id(category_id)
        if category is None:
            raise HTTPException(status_code=404, detail=f"KPI Category with ID {category_id} not found")
        return category

    def list_kpi_categories(self) -> List[KPICategory]:
        """Retrieves all KPI categories."""
        return self.kpi_repository.list_categories()

    # --- KPI Methods ---

    def create_kpi(self, kpi_data: KPI) -> KPI:
        """Creates a new KPI."""
        self._check_category_exists(kpi_data.category_id) # Validate category exists
        try:
            return self.kpi_repository.create_kpi(kpi_data)
        except Exception as e:
            print(f"Error creating KPI in service: {e}")
            raise HTTPException(status_code=500, detail="Failed to create KPI.")

    def get_kpi(self, kpi_id: int) -> KPI:
        """Retrieves a specific KPI."""
        kpi = self.kpi_repository.get_kpi_by_id(kpi_id)
        if kpi is None:
            raise HTTPException(status_code=404, detail=f"KPI with ID {kpi_id} not found")
        return kpi

    def list_kpis(self) -> List[KPI]:
        """Retrieves all KPIs."""
        return self.kpi_repository.list_kpis()

    # --- KPI Result Methods ---

    def create_kpi_result(self, result_data: KPIResult) -> KPIResult:
        """Creates a new KPI result."""
        self._check_user_exists(result_data.user_id)
        self._check_kpi_exists(result_data.kpi_id)
        # Add validation for period format, target/actual values if needed
        try:
            return self.kpi_repository.create_result(result_data)
        except Exception as e:
            print(f"Error creating KPI result in service: {e}")
            raise HTTPException(status_code=500, detail="Failed to create KPI result.")

    def get_kpi_result(self, result_id: int) -> KPIResult:
        """Retrieves a specific KPI result."""
        result = self.kpi_repository.get_result_by_id(result_id)
        if result is None:
            raise HTTPException(status_code=404, detail=f"KPI Result with ID {result_id} not found")
        return result

    def list_kpi_results(self, user_id: int | None = None, kpi_id: int | None = None) -> List[KPIResult]:
        """Retrieves KPI results, potentially filtered."""
        # Add validation/authorization checks here if needed (e.g., can user X see results for user Y?)
        return self.kpi_repository.list_results(user_id=user_id, kpi_id=kpi_id)

    # Add update/delete methods as needed, including necessary business logic