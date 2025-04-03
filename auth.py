from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from models import User
from services.user_service import UserService

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    user_service: UserService = Depends(UserService)
) -> User:
    """
    Retrieves the currently authenticated user based on the Bearer token.
    Raises 401 if token is invalid or user not found.
    """
    print("Credentials: ", credentials)
    try:
        token = credentials.credentials
        # In a real app, decode JWT token here to get user_id
        # For now, extract user_id from our dummy token format: "dummy_token_for_username"
        username = token.replace("dummy_token_for_", "")
        user = user_service.get_user_by_username(username)
        print(token)

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

# --- Authorization Dependency ---

async def require_admin_role(current_user: User = Depends(get_current_user)):
    """
    Dependency that checks if the current user has the 'admin' role.
    Raises 403 Forbidden if the user is not an admin.
    """
    print(f"Checking admin role for user: {current_user.username}, Role: {current_user.role}") # Debug print
    if current_user.role.lower() != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operation requires administrator privileges",
        )
    return current_user # Return the user object if check passes

# --- Dependency for any authenticated user ---
async def require_authenticated_user(current_user: User = Depends(get_current_user)):
    """
    Simple dependency that ensures a user is authenticated (identified via get_current_user).
    Useful for endpoints accessible by any logged-in user.
    Relies on get_current_user to raise 401 if authentication fails.
    """
    # If get_current_user succeeds, the user is considered authenticated.
    # No further checks needed here unless checking for active status, etc.
    print(f"User authenticated: {current_user.username}") # Optional debug print
    return current_user