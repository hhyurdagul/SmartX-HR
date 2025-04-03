from models import TrainingCourse, UserTrainingProgress
from repositories.training_repository import TrainingRepository
from repositories.user_repository import UserRepository # To validate user IDs
from fastapi import Depends, HTTPException
from typing import List, Dict, Any

class TrainingService:
    """Encapsulates business logic related to Training Categories, Courses, and User Progress."""

    def __init__(
        self,
        training_repository: TrainingRepository = Depends(),
        user_repository: UserRepository = Depends()
    ):
        self.training_repository = training_repository
        self.user_repository = user_repository

    def _check_user_exists(self, user_id: int):
        """Helper to check if a user exists."""
        user = self.user_repository.get_user_by_id(user_id)
        if user is None:
            raise HTTPException(status_code=404, detail=f"User with ID {user_id} not found")
        return user

    def _check_course_exists(self, course_id: int):
        """Helper to check if a Training Course exists."""
        course = self.training_repository.get_course_by_id(course_id)
        if course is None:
            raise HTTPException(status_code=404, detail=f"Training Course with ID {course_id} not found")
        return course

    def _check_category_exists(self, category_id: int):
        """Helper to check if a Training Category exists."""
        category = self.training_repository.get_category_by_id(category_id)
        if category is None:
            raise HTTPException(status_code=404, detail=f"Training Category with ID {category_id} not found")
        return category

    # --- Training Course Methods ---

    def create_training_course(self, course_data: TrainingCourse) -> TrainingCourse:
        """Creates a new training course."""
        try:
            return self.training_repository.create_course(course_data)
        except Exception as e:
            print(f"Error creating training course in service: {e}")
            raise HTTPException(status_code=500, detail="Failed to create training course.")

    def get_training_course(self, course_id: int) -> TrainingCourse:
        """Retrieves a specific training course."""
        course = self.training_repository.get_course_by_id(course_id)
        if course is None:
            raise HTTPException(status_code=404, detail=f"Training Course with ID {course_id} not found")
        return course

    def list_training_courses(self, category_id: int | None = None) -> List[TrainingCourse]:
        """Retrieves training courses, optionally filtered by category."""
        if category_id is not None:
            self._check_category_exists(category_id) # Validate category if provided
        return self.training_repository.list_courses(category_id=category_id)

    # --- User Training Progress Methods ---

    def create_user_training_progress(self, progress_data: UserTrainingProgress) -> UserTrainingProgress:
        """Creates a new user training progress record (enrollment)."""
        self._check_user_exists(progress_data.user_id)
        self._check_course_exists(progress_data.training_course_id)
        # Add validation: check if user is already enrolled in this course?
        # Add validation for date format, percentage range (0-100) etc.
        if not (0.0 <= progress_data.completion_percentage <= 100.0):
             raise HTTPException(status_code=400, detail="Completion percentage must be between 0.0 and 100.0")
        progress_data.is_completed = (progress_data.completion_percentage == 100.0) # Ensure consistency

        try:
            return self.training_repository.create_progress(progress_data)
        except Exception as e:
            print(f"Error creating user training progress in service: {e}")
            raise HTTPException(status_code=500, detail="Failed to create user training progress.")

    def get_user_training_progress(self, progress_id: int) -> UserTrainingProgress:
        """Retrieves a specific user training progress record."""
        progress = self.training_repository.get_progress_by_id(progress_id)
        if progress is None:
            raise HTTPException(status_code=404, detail=f"User Training Progress with ID {progress_id} not found")
        return progress

    def list_user_training_progress(self, user_id: int | None = None, course_id: int | None = None) -> List[UserTrainingProgress]:
        """Retrieves user training progress records, potentially filtered."""
        # Add authorization checks if needed
        if user_id is not None:
            self._check_user_exists(user_id)
        if course_id is not None:
            self._check_course_exists(course_id)
        return self.training_repository.list_progress(user_id=user_id, course_id=course_id)

    def update_user_training_progress(self, progress_id: int, progress_update_data: Dict[str, Any]) -> UserTrainingProgress:
        """Updates a user's training progress."""
        # Check if progress record exists first
        existing_progress = self.get_user_training_progress(progress_id) # Handles 404

        # Validate incoming data (e.g., percentage range)
        if 'completion_percentage' in progress_update_data:
            percentage = progress_update_data['completion_percentage']
            if not isinstance(percentage, (int, float)) or not (0.0 <= percentage <= 100.0):
                 raise HTTPException(status_code=400, detail="Completion percentage must be a number between 0.0 and 100.0")
            # Automatically update is_completed based on percentage
            progress_update_data['is_completed'] = (percentage == 100.0)
        elif 'is_completed' in progress_update_data and progress_update_data['is_completed'] is True:
             # If setting completed directly, ensure percentage is 100
             if existing_progress.completion_percentage != 100.0:
                 progress_update_data['completion_percentage'] = 100.0

        # Prevent changing user_id or training_course_id? Decide based on requirements.
        if 'user_id' in progress_update_data or 'training_course_id' in progress_update_data:
            raise HTTPException(status_code=400, detail="Cannot change user_id or training_course_id of an existing progress record.")

        try:
            updated_progress = self.training_repository.update_progress(progress_id, progress_update_data)
            if updated_progress is None:
                 # Should have been caught by get_user_training_progress, but as fallback
                 raise HTTPException(status_code=404, detail=f"User Training Progress with ID {progress_id} not found during update.")
            return updated_progress
        except Exception as e:
            print(f"Error updating user training progress in service: {e}")
            raise HTTPException(status_code=500, detail="Failed to update user training progress.")

    # Add delete methods if required