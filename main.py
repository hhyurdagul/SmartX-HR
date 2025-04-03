from fastapi import FastAPI
import db_utils # For database initialization
# Import all routers
from routers import user_router, leave_router, kpi_router, training_router, team_router, auth_router

# Create the main FastAPI application instance
app = FastAPI(
    title="SmartX HR Assistant API",
    description="API for managing HR-related tasks like leaves, KPIs, training, and teams.",
    version="1.0.0" # Start with a version
)

# --- Database Initialization ---
# This runs once when the application starts
@app.on_event("startup")
async def startup_event():
    print("Application startup: Initializing database...")
    db_utils.initialize_database()
    print("Database initialization complete.")

# --- Include Routers ---
# Mount the routers defined in separate files
# FastAPI handles dependency injection for services/repositories within these routers

app.include_router(user_router.router)
app.include_router(leave_router.router)
app.include_router(kpi_router.router)
app.include_router(training_router.router)
app.include_router(team_router.router)
app.include_router(auth_router.router) # Include the new auth router


# --- Root Endpoint (Optional) ---
@app.get("/", tags=["Root"])
async def read_root():
    """Provides a simple welcome message."""
    return {"message": "Welcome to the SmartX HR Assistant API"}

# All specific endpoint definitions previously in this file have been moved
# to their respective router files in the 'routers' directory.

# To run the application (using uvicorn):
# uvicorn main:app --reload