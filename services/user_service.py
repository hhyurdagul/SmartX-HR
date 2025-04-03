from models import User, UserCreate, UserLogin # Import UserCreate and UserLogin
from repositories.user_repository import UserRepository
from fastapi import Depends, HTTPException, status # Import status for HTTP codes

class UserService:
    """Encapsulates business logic related to users."""

    def __init__(self, user_repository: UserRepository = Depends()):
        """
        Initializes the UserService with a UserRepository dependency.
        FastAPI's Depends() will handle injecting the repository instance.
        """
        self.user_repository = user_repository

    def get_user(self, user_id: int) -> User:
        """
        Retrieves a user by ID. Includes basic 'not found' handling.
        """
        user = self.user_repository.get_user_by_id(user_id)
        if user is None:
            # Raise HTTPException here, which the API layer can directly use
            raise HTTPException(status_code=404, detail=f"User with ID {user_id} not found")
        # The repository returns the User model including password here
        return user

    def get_user_by_username(self, username: str) -> User:
        """
        Retrieves a user by username. Includes basic 'not found' handling.
        """
        user = self.user_repository.get_user_by_username_or_email(username)
        if user is None:
            # Raise HTTPException here, which the API layer can directly use
            raise HTTPException(status_code=404, detail=f"User with username {username} not found")
        # The repository returns the User model including password here
        return user

    # Renamed to register_user and takes UserCreate model
    def register_user(self, user_data: UserCreate) -> User:
        """
        Registers a new user. Handles basic validation and potential conflicts.
        Returns the created user details (excluding password).
        """
        # Basic validation example (could be more extensive)
        if not user_data.email or "@" not in user_data.email:
             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid email format provided.")
        if not user_data.username:
             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username cannot be empty.")
        if not user_data.password or len(user_data.password) < 4: # Example: Basic password length check
             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password must be at least 4 characters long.")
        # Ensure role is set (e.g., default to 'employee' if not provided or invalid?)
        if not user_data.role:
            user_data.role = "employee" # Default role

        try:
            # create_user now expects UserCreate and handles password storage
            created_user = self.user_repository.create_user(user_data)
            # The repository returns a User model without the password
            return created_user
        except Exception as e: # Catch potential repo errors (like IntegrityError)
             print(f"Error creating user in service: {e}")
             # Check for unique constraint error specifically
             if "UNIQUE constraint failed" in str(e):
                 # Determine if it was email or username if possible, or give generic message
                 raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username or email already exists.")
             raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create user due to a database error.")

    def authenticate_user(self, login_data: UserLogin) -> User | None:
        """
        Authenticates a user by username/email and plain text password comparison.
        Returns the user object if authentication is successful, otherwise None.
        WARNING: Plain text password comparison is highly insecure!
        """
        user = self.user_repository.get_user_by_username_or_email(login_data.username)
        if not user:
            print(f"Authentication failed: User '{login_data.username}' not found.")
            return None # User not found

        # Direct plain text comparison (INSECURE!)
        if user.password != login_data.password:
            print(f"Authentication failed: Incorrect password for user '{login_data.username}'.")
            return None # Incorrect password

        print(f"Authentication successful for user '{login_data.username}'.")
        # Authentication successful, return user object (repo includes password needed for auth.py simulation)
        return user

    # Add other user-related business logic methods here
    # e.g., update_user_profile, deactivate_user, etc.