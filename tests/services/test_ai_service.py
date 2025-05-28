import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock

# Assuming application code (services, ollama_client) is at the root
# If it's in an 'app' directory, it would be:
# from app.services.ai_service import AIService
# from app.ollama_client import OllamaClient
from services.ai_service import AIService
from ollama_client import OllamaClient

@pytest.fixture
def ai_service_mocked_ollama():
    """
    Pytest fixture that provides an AIService instance with a mocked OllamaClient.
    The OllamaClient's `generate` method is an AsyncMock.
    """
    mock_ollama_client = MagicMock(spec=OllamaClient)
    mock_ollama_client.generate = AsyncMock()
    
    # Instantiate AIService
    # AIService constructor might take arguments if it changes, adjust here if needed.
    service_instance = AIService() 
    
    # Replace the actual ollama_client with the mock
    service_instance.ollama_client = mock_ollama_client
    
    return service_instance

async def test_decide_leave_request_statuses_for_team_callable(ai_service_mocked_ollama: AIService):
    """
    Tests that decide_leave_request_statuses_for_team is callable and returns expected structure.
    """
    dummy_team_leave_requests = [{'id': 1, 'reason': 'Vacation'}]
    dummy_team_id_context = "Team Alpha"

    # Set a basic return value for the mocked ollama_client.generate
    ai_service_mocked_ollama.ollama_client.generate.return_value = "ID: 1\nSuggested Status: approved\nReasoning: OK\n---"
    
    result = await ai_service_mocked_ollama.decide_leave_request_statuses_for_team(
        dummy_team_leave_requests, 
        dummy_team_id_context
    )
    
    assert result is not None
    assert isinstance(result, list)
    if result: # If the list is not empty
        assert 'id' in result[0]
        assert 'status' in result[0]
        assert 'ai_reasoning' in result[0]

async def test_recommend_training_courses_callable(ai_service_mocked_ollama: AIService):
    """
    Tests that recommend_training_courses is callable and returns expected structure.
    """
    dummy_user_details = {'role': 'Engineer', 'start_date': '2022-01-01', 'career_goals': 'Become a Senior Engineer'}
    dummy_user_kpis = [{'kpi_name': 'Projects Completed', 'target': 5, 'actual_value': 3, 'period': 'Q1'}]
    dummy_user_trainings = [{'course_name': 'Intro to Python', 'enrollment_date': '2023-01-15'}]
    dummy_all_courses = [{'training_course_id': 101, 'course_name': 'Advanced Python', 'description': 'Deep dive into Python.'}]

    # Set a basic return value for the mocked ollama_client.generate
    ai_service_mocked_ollama.ollama_client.generate.return_value = "Course ID: 101\nCourse Name: Advanced Python\nReasoning: Based on KPIs and goals.\n---"
    
    result = await ai_service_mocked_ollama.recommend_training_courses(
        dummy_user_details,
        dummy_user_kpis,
        dummy_user_trainings,
        dummy_all_courses
    )
    
    assert result is not None
    assert 'recommendations' in result
    assert isinstance(result['recommendations'], list)
    # Example further check if recommendations list is not empty
    # if result['recommendations']:
    #     assert 'course_name' in result['recommendations'][0]

async def test_assess_kpi_results_callable(ai_service_mocked_ollama: AIService):
    """
    Tests that assess_kpi_results is callable and returns expected structure.
    """
    dummy_kpi_results_data = [{
        'result_id': 1, 
        'kpi_name': 'Tasks Completed', 
        'kpi_description': 'Number of tasks completed on time.',
        'period': 'Q1-2024', 
        'unit': 'tasks', 
        'target': 10, 
        'actual_value': 8
    }]
    dummy_user_details = {'role': 'Developer', 'email': 'dev@example.com'}

    # Set a basic return value for the mocked ollama_client.generate
    ai_service_mocked_ollama.ollama_client.generate.return_value = "Result ID: 1\nAssessment: Meets Expectations\nReasoning: Close to target.\n---"
        
    result = await ai_service_mocked_ollama.assess_kpi_results(
        dummy_kpi_results_data,
        dummy_user_details
    )
    
    assert result is not None
    assert 'assessed_kpis' in result
    assert isinstance(result['assessed_kpis'], list)
    # Example further check if assessed_kpis list is not empty
    # if result['assessed_kpis']:
    #     assert 'result_id' in result['assessed_kpis'][0]
    #     assert 'ai_assessment' in result['assessed_kpis'][0]
    #     assert 'ai_reasoning' in result['assessed_kpis'][0]

# To run these tests (if this file is executed directly, which is not typical for pytest):
# if __name__ == "__main__":
#     # This is more for demonstration; use `pytest` command in terminal
#     async def main_run():
#         # Manually create fixture for direct run (not recommended for real tests)
#         mock_ollama = MagicMock(spec=OllamaClient)
#         mock_ollama.generate = AsyncMock()
#         service = AIService()
#         service.ollama_client = mock_ollama
#
#         await test_decide_leave_request_statuses_for_team_callable(service)
#         await test_recommend_training_courses_callable(service)
#         await test_assess_kpi_results_callable(service)
#         print("Basic callable tests completed (manual run).")
#
#     asyncio.run(main_run())
