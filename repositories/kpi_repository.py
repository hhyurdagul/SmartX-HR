from models import KPI, KPICategory, KPIResult
from .base_repository import get_db_connection
from typing import List
import sqlite3

class KpiRepository:
    """Handles database operations for KPI, KPICategory, and KPIResult entities."""

    # --- KPI Category Methods ---

    def create_category(self, category: KPICategory) -> KPICategory:
        """Creates a new KPI category."""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO kpi_categories (category_name) VALUES (?)", (category.category_name,))
                conn.commit()
                category_id = cursor.lastrowid
                return KPICategory(category_id=category_id, **category.dict(exclude={'category_id'}))
        except sqlite3.Error as e:
            print(f"Database Error creating KPI category: {e}")
            raise

    def list_categories(self) -> List[KPICategory]:
        """Retrieves all KPI categories."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM kpi_categories ORDER BY category_name")
            rows = cursor.fetchall()
            return [KPICategory(**dict(row)) for row in rows]

    def get_category_by_id(self, category_id: int) -> KPICategory | None:
        """Retrieves a KPI category by its ID."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM kpi_categories WHERE category_id = ?", (category_id,))
            row = cursor.fetchone()
            if row:
                return KPICategory(**dict(row))
            return None

    # --- KPI Methods ---

    def create_kpi(self, kpi: KPI) -> KPI:
        """Creates a new KPI."""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO kpis (category_id, kpi_name, unit, description) VALUES (?, ?, ?, ?)",
                    (kpi.category_id, kpi.kpi_name, kpi.unit, kpi.description),
                )
                conn.commit()
                kpi_id = cursor.lastrowid
                return KPI(kpi_id=kpi_id, **kpi.dict(exclude={'kpi_id'}))
        except sqlite3.Error as e:
            print(f"Database Error creating KPI: {e}")
            raise

    def list_kpis(self) -> List[KPI]:
        """Retrieves all KPIs."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            # Consider joining with categories if needed often
            cursor.execute("SELECT * FROM kpis ORDER BY kpi_name")
            rows = cursor.fetchall()
            return [KPI(**dict(row)) for row in rows]

    def get_kpi_by_id(self, kpi_id: int) -> KPI | None:
        """Retrieves a KPI by its ID."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM kpis WHERE kpi_id = ?", (kpi_id,))
            row = cursor.fetchone()
            if row:
                return KPI(**dict(row))
            return None

    # --- KPI Result Methods ---

    def create_result(self, result: KPIResult) -> KPIResult:
        """Creates a new KPI result."""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO kpi_results (kpi_id, user_id, period, target, actual_value, ai_assessment, ai_reasoning, ai_error_message) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        result.kpi_id, 
                        result.user_id, 
                        result.period, 
                        result.target, 
                        result.actual_value,
                        result.ai_assessment, # Will be None on initial creation
                        result.ai_reasoning,   # Will be None on initial creation
                        result.ai_error_message # Will be None on initial creation
                    ),
                )
                conn.commit()
                result_id = cursor.lastrowid
                return KPIResult(result_id=result_id, **result.dict(exclude={'result_id'}))
        except sqlite3.Error as e:
            print(f"Database Error creating KPI result: {e}")
            raise

    def list_results(self, user_id: int | None = None, kpi_id: int | None = None) -> List[KPIResult]:
        """Retrieves KPI results, optionally filtered by user or KPI."""
        query = "SELECT * FROM kpi_results"
        params = []
        conditions = []
        if user_id is not None:
            conditions.append("user_id = ?")
            params.append(user_id)
        if kpi_id is not None:
            conditions.append("kpi_id = ?")
            params.append(kpi_id)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        query += " ORDER BY period DESC, user_id" # Example ordering

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [KPIResult(**dict(row)) for row in rows]

    def get_result_by_id(self, result_id: int) -> KPIResult | None:
        """Retrieves a KPI result by its ID."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM kpi_results WHERE result_id = ?", (result_id,))
            row = cursor.fetchone()
            if row:
                return KPIResult(**dict(row))
            return None

    def update_kpi_result_ai_assessment(self, result_id: int, ai_assessment_data: Dict) -> KPIResult | None:
        """Updates the AI assessment fields of a specific KPI result."""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    UPDATE kpi_results 
                    SET ai_assessment = ?, 
                        ai_reasoning = ?, 
                        ai_error_message = ?
                    WHERE result_id = ?
                    """,
                    (
                        ai_assessment_data.get('ai_assessment'),
                        ai_assessment_data.get('ai_reasoning'),
                        ai_assessment_data.get('ai_error_message'),
                        result_id
                    )
                )
                conn.commit()
                if cursor.rowcount == 0:
                    return None # Indicate result not found or no change needed
            # Return the updated result data
            return self.get_result_by_id(result_id)
        except sqlite3.Error as e:
            print(f"Database Error updating KPI result AI assessment: {e}")
            raise

    # Add update/delete methods for categories, kpis, results if required