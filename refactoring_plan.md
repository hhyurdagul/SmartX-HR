# Codebase Refactoring Plan

## 1. Current State Analysis

Based on the review of `main.py`, `models.py`, and `db_utils.py`:

*   **`main.py` (API Layer):** Acts as the API layer using FastAPI. Defines all endpoints and directly calls functions from `db_utils.py`. This leads to tight coupling and mixes API concerns with data orchestration.
*   **`models.py` (Data Structures):** Defines Pydantic models used for API validation and database return types. Good separation of data structure definitions.
*   **`db_utils.py` (Data Access):** Contains all database logic (schema initialization, connection handling, CRUD functions). Monolithic, tightly coupled to SQLite and Pydantic models.

## 2. Key Issues Identified

1.  **Tight Coupling:** `main.py` directly depends on `db_utils.py` implementation details.
2.  **Poor Separation of Concerns (SoC):**
    *   API layer handles routing, validation, *and* data orchestration.
    *   Data access layer handles schema, connections, and CRUD for *all* entities.
    *   Business logic is scattered or missing.
3.  **Limited Testability:** Unit testing API endpoints is difficult without a live database or extensive mocking.
4.  **Maintainability & Scalability:** Modifying or adding features requires changes in large, monolithic files.
5.  **SOLID Principle Violations:** Primarily SRP (Single Responsibility Principle) and DIP (Dependency Inversion Principle).

## 3. Proposed Architecture & Refactoring Plan

Introduce clear layers with distinct responsibilities:

**Target Architecture Diagram:**

```mermaid
graph TD
    A[API Layer (main.py / routers)] --> B(Service Layer);
    B --> C(Repository Layer);
    C --> D[(Database)];
    M[Models (models.py)] --> A;
    M --> B;
    M --> C;

    subgraph API Layer
        direction LR
        R1[User Router]
        R2[Leave Router]
        R3[...]
    end

    subgraph Service Layer
        direction LR
        S1[User Service]
        S2[Leave Service]
        S3[...]
    end

    subgraph Repository Layer
        direction LR
        P1[User Repository]
        P2[Leave Repository]
        P3[...]
    end

    A -- Uses --> M;
    B -- Uses --> M;
    C -- Uses --> M;
```

**Detailed Recommendations:**

1.  **Introduce a Service Layer (`services/`):**
    *   Encapsulate business logic and orchestrate operations.
    *   Act as an intermediary between API and Repository layers.
    *   Example: `services/leave_service.py` with `LeaveService` class.

2.  **Implement the Repository Pattern (`repositories/`):**
    *   Abstract data persistence details.
    *   Refactor `db_utils.py` into multiple repository classes (e.g., `repositories/user_repository.py`).
    *   Handle SQL queries/ORM calls and map data to/from models.

3.  **Refactor the API Layer (`main.py` & `routers/`):**
    *   Use FastAPI `APIRouter` to split endpoints by feature (e.g., `routers/leave_router.py`).
    *   Keep endpoint functions lean, calling Service methods.

4.  **Utilize Dependency Injection (FastAPI `Depends`):**
    *   Inject Repositories into Services and Services into Routers.
    *   Manage dependencies and improve testability.

5.  **Database Initialization:**
    *   Move `initialize_database` logic to a separate module (e.g., `database.py`), called on startup.

## 4. Benefits of Proposed Structure

*   **Improved Modularity:** Code organized by feature and layer.
*   **Enhanced Testability:** Layers can be tested independently.
*   **Increased Maintainability:** Changes are localized.
*   **Better Scalability:** Easier to add/scale features.
*   **Flexibility:** Easier to swap implementations (e.g., database).
*   **Adherence to SOLID:** Better SRP, OCP, ISP, and DIP.