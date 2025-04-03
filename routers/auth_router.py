from fastapi import APIRouter, Depends, HTTPException, status
from models import User, UserCreate, UserLogin, Token # Import necessary models
from services.user_service import UserService

router = APIRouter(
    tags=["Authentication"] # Tag for OpenAPI documentation
)

@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register_new_user(
    user_data: UserCreate,
    user_service: UserService = Depends(UserService)
):
    """
    Registers a new user. Requires username, email, password, role, start_date.
    Returns the created user details (excluding password).
    Raises 409 Conflict if username or email already exists.
    """
    # The user_service.register_user handles validation, creation, and errors
    # It returns a User model (without password) on success
    return user_service.register_user(user_data)


@router.post("/login", response_model=Token) # Define response model (e.g., a dummy token)
async def login_for_access_token(
    login_data: UserLogin,
    user_service: UserService = Depends(UserService)
):
    """
    Authenticates a user and returns a dummy access token.
    Uses plain text password comparison (INSECURE!).
    """
    user = user_service.authenticate_user(login_data)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # --- Token Generation (Dummy) ---
    # In a real app, you would generate a JWT here based on user.user_id or user.username
    # For now, just return a dummy token
    access_token = f"dummy_token_for_{user.username}"
    return Token(access_token=access_token, token_type="bearer")

# Note: The actual authentication enforcement (checking tokens on protected routes)
# would typically happen in the `get_current_user` dependency in `auth.py`,
# which currently just simulates fetching user 1.