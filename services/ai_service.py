# services/ai_service.py

from typing import Dict, List # Added List
from ..ollama_client import OllamaClient # Assuming ollama_client.py is in the parent directory
from datetime import datetime # Added datetime import
import re # For parsing response

class AIService:
    def __init__(self):
        self.ollama_client = OllamaClient()

    async def prioritize_leave_request(
        self,
        leave_request_data: Dict,
        user_data: Dict,
        team_context: Dict
    ) -> Dict:
        """
        Prioritizes a leave request based on user data, team context, and the leave request itself
        by calling the Ollama client.
        """
        default_error_response = {
            "priority_score": 0.0,
            "suggested_priority": "Error",
            "reasoning": "Default error response",
            "error_message": "An unspecified error occurred."
        }

        # 1. Date Parsing and Duration Calculation
        try:
            start_date_str = leave_request_data.get('start_date')
            end_date_str = leave_request_data.get('end_date')
            if not start_date_str or not end_date_str:
                raise ValueError("Start or end date missing.")
            
            start_date_obj = datetime.strptime(start_date_str, "%Y-%m-%d")
            end_date_obj = datetime.strptime(end_date_str, "%Y-%m-%d")
            duration = (end_date_obj - start_date_obj).days + 1
            if duration <= 0:
                raise ValueError("End date must be after start date.")
        except ValueError as e:
            error_msg = f"Invalid date format or range: {str(e)}"
            print(f"AIService Error: {error_msg}")
            return {
                "priority_score": 0.0,
                "suggested_priority": "Error",
                "reasoning": error_msg,
                "error_message": error_msg
            }

        # 2. Prompt Construction
        formatted_prompt = f"""
Analyze the following leave request and provide a priority (Low, Medium, High) and a brief reasoning.
Output format:
Priority: [High|Medium|Low]
Reasoning: [Your reasoning here]

Leave Request Details:
- User ID: {user_data.get('user_id', 'N/A')}
- User Role: {user_data.get('role', 'N/A')}
- User Start Date (Employment): {user_data.get('start_date', 'N/A')}
- Leave Type: {leave_request_data.get('leave_type', 'N/A')}
- Request Start Date: {start_date_str}
- Request End Date: {end_date_str}
- Duration (days): {duration}
- Reason: {leave_request_data.get('reason', 'N/A')}
- Current Leave Balance (days): {user_data.get('leave_balance', 'N/A')}

Team Context:
- Team ID: {team_context.get('team_id', 'N/A')}
- Number of Members on Leave during this period: {len(team_context.get('other_leaves_in_period', []))}
- Critical Projects/Deadlines during this period: {'Yes' if len(team_context.get('current_projects', [])) > 0 else 'No'}
"""
        print(f"AIService: Sending prompt to Ollama:\n{formatted_prompt}")

        # 3. Ollama Call
        response_text = None
        try:
            response_text = await self.ollama_client.generate(prompt=formatted_prompt)
            if response_text is None:
                error_message = "Ollama client failed to get a response (returned None)."
                print(f"AIService Error: {error_message}")
                return {
                    "priority_score": 0.0,
                    "suggested_priority": "Error",
                    "reasoning": "AI client did not return a response.",
                    "error_message": error_message
                }
        except Exception as e:
            error_message = f"Error calling Ollama: {str(e)}"
            print(f"AIService Error: {error_message}")
            return {
                "priority_score": 0.0,
                "suggested_priority": "Error",
                "reasoning": f"AI client call failed: {str(e)}",
                "error_message": error_message
            }

        # 4. Response Parsing
        print(f"AIService: Received response from Ollama:\n{response_text}")
        parsed_priority_str = "N/A"
        parsed_reasoning = "Could not parse AI response."
        priority_score = 0.0

        # Normalize response text for easier parsing
        response_lines = response_text.lower().splitlines()
        
        # Priority Parsing
        for line in response_lines:
            if line.startswith("priority:"):
                parsed_priority_str = line.replace("priority:", "").strip()
                if parsed_priority_str == "high":
                    priority_score = 0.9
                elif parsed_priority_str == "medium":
                    priority_score = 0.5
                elif parsed_priority_str == "low":
                    priority_score = 0.1
                else: # If AI gives something unexpected
                    parsed_priority_str = "Unknown: " + parsed_priority_str 
                    priority_score = 0.0 
                break
        
        # Reasoning Parsing
        reasoning_started = False
        reasoning_lines = []
        for line in response_text.splitlines(): # Use original case for reasoning
            if line.lower().startswith("reasoning:"):
                reasoning_started = True
                # Remove "Reasoning:" prefix and strip whitespace
                cleaned_line = re.sub(r'^[Rr][Ee][Aa][Ss][Oo][Nn][Ii][Nn][Gg]:\s*', '', line).strip()
                if cleaned_line: # Add if there's content after "Reasoning:" on the same line
                    reasoning_lines.append(cleaned_line)
                continue
            if reasoning_started:
                # Stop if another known section or excessive lines (simple heuristic)
                if line.lower().startswith("priority:") or len(reasoning_lines) > 10: 
                    break
                reasoning_lines.append(line.strip())
        
        if reasoning_lines:
            parsed_reasoning = " ".join(reasoning_lines)
        elif not reasoning_started and response_text: # Fallback if "Reasoning:" tag not found
             parsed_reasoning = response_text # Use the whole response as reasoning

        return {
            "priority_score": priority_score,
            "suggested_priority": parsed_priority_str,
            "reasoning": parsed_reasoning,
            "error_message": None
        }

# Example Usage (for testing purposes, can be removed later - ensure it's async now):
# if __name__ == "__main__":
#     import asyncio
#
#     async def main(): # Ensure main is async
#         ai_service = AIService()
#
#         # Dummy data for testing
#         dummy_leave_request_ok = {
#             "user_id": "user001",
#             "leave_type": "Vacation",
#             "start_date": "2024-09-15",
#             "end_date": "2024-09-20",
#             "reason": "Annual vacation for travel"
#         }
#         dummy_leave_request_bad_date = {
#             "user_id": "user002",
#             "leave_type": "Sick",
#             "start_date": "2024-08-invalid", # Invalid date
#             "end_date": "2024-08-20",
#             "reason": "Flu"
#         }
#         dummy_user = {
#             "user_id": "user001", # Matched with leave_request_data
#             "role": "Software Engineer",
#             "start_date": "2020-01-15", # Employment start date
#             "leave_balance": 15
#         }
#         dummy_team_context = {
#             "team_id": "teamA",
#             "current_projects": ["Project Alpha Q3 deadline"], # Critical projects
#             "other_leaves_in_period": [{"user_id": "user003", "start": "2024-09-16", "end": "2024-09-18"}] # Another member on leave
#         }
#
#         print("--- Testing OK Request ---")
#         prioritization_result_ok = await ai_service.prioritize_leave_request(
#             dummy_leave_request_ok,
#             dummy_user,
#             dummy_team_context
#         )
#         print("\nPrioritization Result (OK):")
#         for key, value in prioritization_result_ok.items():
#             print(f"  {key}: {value}")
#
#         print("\n--- Testing Bad Date Request ---")
#         prioritization_result_bad_date = await ai_service.prioritize_leave_request(
#             dummy_leave_request_bad_date,
#             dummy_user,
#             dummy_team_context
#         )
#         print("\nPrioritization Result (Bad Date):")
#         for key, value in prioritization_result_bad_date.items():
#             print(f"  {key}: {value}")
#
#     asyncio.run(main())

    # async def prioritize_leave_requests_batch(self, leave_requests_details: List[Dict]) -> List[Dict]:
    #     """
    #     Prioritizes a batch of leave requests using a single comparative call to the Ollama client.
    #     """
    #     results = []
    #     request_details_for_prompt = []
    #     processed_request_ids = set()
    #
    #     # 1. Pre-process and validate input, prepare prompt segments
    #     for req_detail in leave_requests_details:
    #         leave_request_id = req_detail.get("leave_request_id")
    #         if leave_request_id is None:
    #             # Handle cases where leave_request_id is missing, though it's expected
    #             results.append({
    #                 "leave_request_id": None, # Or some placeholder
    #                 "ai_priority_score": 0.0,
    #                 "ai_suggested_priority": "Error",
    #                 "ai_reasoning": "Missing leave_request_id in input.",
    #                 "ai_error_message": "Missing leave_request_id in input."
    #             })
    #             continue
    #        
    #         processed_request_ids.add(leave_request_id) # Track all incoming IDs
    #
    #         try:
    #             start_date_str = req_detail.get('leave_start_date')
    #             end_date_str = req_detail.get('leave_end_date')
    #             if not start_date_str or not end_date_str:
    #                 raise ValueError("Start or end date missing.")
    #            
    #             start_date_obj = datetime.strptime(start_date_str, "%Y-%m-%d")
    #             end_date_obj = datetime.strptime(end_date_str, "%Y-%m-%d")
    #             duration = (end_date_obj - start_date_obj).days + 1
    #             if duration <= 0:
    #                 raise ValueError("End date must be after start date.")
    #            
    #             req_detail['calculated_duration'] = duration # Store for prompt
    #             request_details_for_prompt.append(req_detail)
    #
    #         except ValueError as e:
    #             error_msg = f"Invalid date format or range for request ID {leave_request_id}: {str(e)}"
    #             print(f"AIService Batch Error: {error_msg}")
    #             results.append({
    #                 "leave_request_id": leave_request_id,
    #                 "ai_priority_score": 0.0,
    #                 "ai_suggested_priority": "Error",
    #                 "ai_reasoning": error_msg,
    #                 "ai_error_message": error_msg
    #             })
    #
    #     if not request_details_for_prompt: # All initial requests had date errors or were empty
    #         # Ensure all original IDs are accounted for if not already in results
    #         for req_id in processed_request_ids:
    #             if not any(r['leave_request_id'] == req_id for r in results):
    #                 results.append({
    #                     "leave_request_id": req_id,
    #                     "ai_priority_score": 0.0,
    #                     "ai_suggested_priority": "Error",
    #                     "ai_reasoning": "Skipped due to earlier batch processing error or no valid data.",
    #                     "ai_error_message": "Skipped due to earlier batch processing error or no valid data."
    #                 })
    #         return results
    #
    #     # 2. Prompt Construction
    #     prompt_header = """You are an HR expert AI. Your task is to analyze a batch of leave requests and provide a priority (Low, Medium, High) and a brief reasoning for each, considering them comparatively.
    # Output the results for EACH request ID provided in the input. Use the following format for each request:
    # ---
    # Request ID: [ID]
    # Priority: [High|Medium|Low]
    # Reasoning: [Your reasoning here]
    # ---
    # """
    #     prompt_body_parts = []
    #     for req in request_details_for_prompt:
    #         prompt_body_parts.append(
    #             f"Request ID: {req['leave_request_id']}\n"
    #             f"- User Role: {req.get('user_role', 'N/A')}\n"
    #             f"- User Start Date (Employment): {req.get('user_start_date', 'N/A')}\n"
    #             f"- Leave Type: {req.get('leave_type', 'N/A')}\n"
    #             f"- Leave Start Date: {req.get('leave_start_date')}\n"
    #             f"- Leave End Date: {req.get('leave_end_date')}\n"
    #             f"- Leave Duration (days): {req['calculated_duration']}\n"
    #             f"- Reason: {req.get('leave_reason', 'N/A')}\n"
    #             # Add other relevant fields if available and useful for comparison
    #             # For example, if team context or project load info is available per request
    #         )
    #    
    #     full_prompt_string = prompt_header + "\n---\n".join(prompt_body_parts) + "\n---" # Ensure final delimiter
    #     print(f"AIService Batch: Sending prompt to Ollama:\n{full_prompt_string}")
    #
    #     # 3. Ollama Call
    #     response_text = None
    #     ollama_error = None
    #     try:
    #         response_text = await self.ollama_client.generate(prompt=full_prompt_string)
    #         if response_text is None:
    #             ollama_error = "Ollama client failed to get a response (returned None)."
    #     except Exception as e:
    #         ollama_error = f"Error calling Ollama: {str(e)}"
    #
    #     if ollama_error:
    #         print(f"AIService Batch Error: {ollama_error}")
    #         # Batch failed, mark all valid (date-wise) requests with this error
    #         for req in request_details_for_prompt:
    #             results.append({
    #                 "leave_request_id": req['leave_request_id'],
    #                 "ai_priority_score": 0.0,
    #                 "ai_suggested_priority": "Error",
    #                 "ai_reasoning": f"Ollama call failed for batch: {ollama_error}",
    #                 "ai_error_message": ollama_error
    #             })
    #         # Add errors for any already processed due to date issues, if not already there
    #         for req_id in processed_request_ids:
    #             if not any(r['leave_request_id'] == req_id for r in results):
    #                  results.append({
    #                     "leave_request_id": req_id,
    #                     "ai_priority_score": 0.0,
    #                     "ai_suggested_priority": "Error",
    #                     "ai_reasoning": "Ollama call failed for batch, and this item might have had prior validation issues.",
    #                     "ai_error_message": ollama_error # Or a more specific message
    #                 })
    #         return results
    #
    #     # 4. Response Parsing
    #     print(f"AIService Batch: Received response from Ollama:\n{response_text}")
    #    
    #     # Split response into segments for each request, using "---" as a top-level separator
    #     # and then "Request ID:" as a more reliable internal marker.
    #     # Using re.split with a lookahead to keep the delimiter might be too complex if "---" is not strictly at the start.
    #     # A simpler approach is to find all occurrences of "Request ID:"
    #    
    #     parsed_ids = set()
    #     for segment_match in re.finditer(r"Request ID:\s*(\S+)", response_text, re.IGNORECASE):
    #         current_req_id_str = segment_match.group(1)
    #         # Attempt to convert to int if your IDs are integers
    #         try:
    #             current_req_id = int(current_req_id_str)
    #         except ValueError:
    #             print(f"AIService Batch Parse Warning: Found non-integer Request ID '{current_req_id_str}' in response. Skipping segment.")
    #             continue # Skip this segment
    #        
    #         parsed_ids.add(current_req_id)
    #
    #         # Define the search space for this ID's priority and reasoning:
    #         # from the start of this "Request ID: ..." to the next "Request ID: ..." or end of text.
    #         segment_start_index = segment_match.start()
    #         next_segment_match = re.search(r"Request ID:\s*\S+", response_text[segment_match.end():], re.IGNORECASE)
    #         segment_end_index = segment_match.end() + next_segment_match.start() if next_segment_match else len(response_text)
    #         segment_content = response_text[segment_start_index:segment_end_index]
    #
    #         priority_str = "N/A"
    #         reasoning_str = "Could not parse AI reasoning."
    #         priority_score = 0.0
    #         item_error_message = None
    #
    #         # Extract Priority
    #         priority_match = re.search(r"Priority:\s*(High|Medium|Low)", segment_content, re.IGNORECASE)
    #         if priority_match:
    #             priority_str = priority_match.group(1).lower()
    #             if priority_str == "high": priority_score = 0.9
    #             elif priority_str == "medium": priority_score = 0.5
    #             elif priority_str == "low": priority_score = 0.1
    #             else: # Should not happen with the regex pattern but as a fallback
    #                 priority_str = "Unknown: " + priority_match.group(1)
    #                 priority_score = 0.0
    #                 item_error_message = f"Unrecognized priority '{priority_match.group(1)}' in response for ID {current_req_id}."
    #         else:
    #             item_error_message = f"Could not parse priority for ID {current_req_id}."
    #             priority_str = "Error"
    #
    #         # Extract Reasoning
    #         reasoning_match = re.search(r"Reasoning:\s*(.+)", segment_content, re.IGNORECASE | re.DOTALL)
    #         if reasoning_match:
    #             # Clean up reasoning: stop at the next "---" or "Request ID:" if they are part of the match
    #             raw_reasoning = reasoning_match.group(1).strip()
    #             raw_reasoning = re.split(r"\n\s*---|\n\s*Request ID:", raw_reasoning, 1)[0].strip()
    #             reasoning_str = raw_reasoning if raw_reasoning else "Reasoning provided but was empty after cleaning."
    #         elif not item_error_message: # Only set this if no priority error
    #              item_error_message = f"Could not parse reasoning for ID {current_req_id}."
    #        
    #         # Check if this ID was part of the valid initial requests
    #         original_request_detail = next((r for r in request_details_for_prompt if r['leave_request_id'] == current_req_id), None)
    #         if original_request_detail:
    #             results.append({
    #                 "leave_request_id": current_req_id,
    #                 "ai_priority_score": priority_score,
    #                 "ai_suggested_priority": priority_str.capitalize() if priority_str not in ["Error", "N/A"] and not priority_str.startswith("Unknown") else priority_str,
    #                 "ai_reasoning": reasoning_str,
    #                 "ai_error_message": item_error_message
    #             })
    #         else:
    #              print(f"AIService Batch Parse Warning: AI provided result for ID {current_req_id} which was not in the valid input batch or had prior date issues. It will be ignored.")
    #
    #
    #     # 5. Ensure all original, valid (date-wise) request IDs have a result, even if parsing failed for them
    #     for req_data in request_details_for_prompt: # Iterate over requests that were sent to Ollama
    #         req_id = req_data['leave_request_id']
    #         if not any(r['leave_request_id'] == req_id for r in results):
    #             results.append({
    #                 "leave_request_id": req_id,
    #                 "ai_priority_score": 0.0,
    #                 "ai_suggested_priority": "Error",
    #                 "ai_reasoning": "AI response did not contain information for this request ID or it was unparseable.",
    #                 "ai_error_message": "AI response did not contain information for this request ID or it was unparseable."
    #             })
    #    
    #     # Finally, ensure all original input IDs (including those with initial validation errors) are in results
    #     all_input_ids = {item.get("leave_request_id") for item in leave_requests_details if item.get("leave_request_id") is not None}
    #     for req_id_orig in all_input_ids:
    #         if not any(r['leave_request_id'] == req_id_orig for r in results):
    #             results.append({
    #                 "leave_request_id": req_id_orig,
    #                 "ai_priority_score": 0.0,
    #                 "ai_suggested_priority": "Error",
    #                 "ai_reasoning": "This request was not processed, likely due to an initial validation error (e.g., date issue) before batch AI call.",
    #                 "ai_error_message": "Not processed by AI due to pre-batch validation error."
    #             })
    #
    #     return results

    async def recommend_training_courses(
        self, 
        user_details: Dict, 
        user_kpis: List[Dict], 
        user_trainings: List[Dict], 
        all_courses: List[Dict]
    ) -> Dict:
        """
        Recommends training courses for a user based on their details, KPIs, past trainings, and available courses.
        """
        recommendations_output = {"recommendations": [], "error_message": None}

        # 1. Prompt Construction
        prompt_parts = [
            "You are an expert career development AI. Your task is to recommend up to 3 training courses for a user based on their profile, performance (KPIs), completed training, and available courses. You can also suggest a 'New Course Idea' if no existing course fits a clear development need.",
            "Output each recommendation in the following format, separated by '---':",
            "Course ID: [Course ID from available list OR 'New Course Idea']",
            "Course Name: [Course Name from available list OR a descriptive name for the new idea]",
            "Reasoning: [Your detailed reasoning for this recommendation, linking it to user's KPIs, role, or goals]",
            "---"
        ]

        # User Details
        prompt_parts.append("\nUser Profile:")
        prompt_parts.append(f"- Role: {user_details.get('role', 'N/A')}")
        prompt_parts.append(f"- Employment Start Date: {user_details.get('start_date', 'N/A')}")
        if user_details.get('career_goals'):
            prompt_parts.append(f"- Stated Career Goals: {user_details['career_goals']}")
        
        # User KPIs
        prompt_parts.append("\nRecent KPI Performance:")
        if user_kpis:
            for kpi in user_kpis:
                kpi_name = kpi.get('kpi_name', 'N/A') # Assuming kpi_name is available directly or fetched
                target = kpi.get('target', 'N/A')
                actual = kpi.get('actual_value', 'N/A')
                period = kpi.get('period', 'N/A')
                prompt_parts.append(f"- KPI: {kpi_name} (Period: {period}, Target: {target}, Actual: {actual})")
        else:
            prompt_parts.append("- No recent KPI data available.")

        # User Past Trainings
        prompt_parts.append("\nCompleted Trainings:")
        if user_trainings:
            for tr in user_trainings:
                course_name = tr.get('course_name', 'N/A') # Assuming course_name is available
                completion_date = tr.get('enrollment_date', 'N/A') # Approximation, or add completion date
                prompt_parts.append(f"- {course_name} (Completed around: {completion_date})")
        else:
            prompt_parts.append("- No completed training data available.")

        # Available Courses
        prompt_parts.append("\nAvailable Training Courses (for reference, you can also suggest new ideas):")
        if all_courses:
            for course in all_courses:
                prompt_parts.append(f"- ID: {course.get('training_course_id', 'N/A')}, Name: {course.get('course_name', 'N/A')}, Description: {course.get('description', 'N/A')[:100]}...") # Truncate desc
        else:
            prompt_parts.append("- No specific list of available courses provided for direct matching (feel free to suggest general or new ideas).")
        
        prompt_parts.append("\nBased on all the above, provide your top 1-3 recommendations:")
        full_prompt_string = "\n".join(prompt_parts)
        print(f"AIService Training Rec: Sending prompt to Ollama:\n{full_prompt_string}")

        # 2. Call Ollama
        response_text = None
        try:
            response_text = await self.ollama_client.generate(prompt=full_prompt_string)
            if response_text is None:
                recommendations_output["error_message"] = "Ollama client failed to get a response (returned None)."
                print(f"AIService Training Rec Error: {recommendations_output['error_message']}")
                return recommendations_output
        except Exception as e:
            error_msg = f"Error calling Ollama for training recommendations: {str(e)}"
            recommendations_output["error_message"] = error_msg
            print(f"AIService Training Rec Error: {error_msg}")
            return recommendations_output

        # 3. Response Parsing
        print(f"AIService Training Rec: Received response from Ollama:\n{response_text}")
        
        # Split by "---" separator, handling potential empty strings from split
        recommendation_blocks = [block.strip() for block in response_text.split("---") if block.strip()]

        if not recommendation_blocks and response_text: # If no "---" but text exists, treat whole as one block
            recommendation_blocks = [response_text.strip()]
            if len(recommendation_blocks[0].splitlines()) < 3: # Heuristic for it being a single recommendation
                 pass # Potentially a single malformed block
            else: # Likely an unparseable response
                 recommendations_output["error_message"] = "Could not parse recommendations from AI response (no valid separators found)."
                 return recommendations_output


        parsed_recommendations = []
        for block_num, block in enumerate(recommendation_blocks):
            course_id_or_idea = "N/A"
            course_name = "N/A"
            reasoning = "Could not parse reasoning."
            
            id_match = re.search(r"Course ID:\s*(.+)", block, re.IGNORECASE)
            if id_match:
                course_id_or_idea = id_match.group(1).strip()

            name_match = re.search(r"Course Name:\s*(.+)", block, re.IGNORECASE)
            if name_match:
                course_name = name_match.group(1).strip()

            reasoning_match = re.search(r"Reasoning:\s*((?:.|\n)+)", block, re.IGNORECASE) # Multi-line reasoning
            if reasoning_match:
                # Clean up reasoning: remove other potential fields if captured
                raw_reasoning = reasoning_match.group(1).strip()
                # Stop if it looks like another field started (e.g., "Course ID:")
                raw_reasoning = re.split(r"\n\s*(?:Course ID:|Course Name:)", raw_reasoning, 1)[0].strip()
                reasoning = raw_reasoning if raw_reasoning else "Reasoning provided but was empty."
            
            # Basic validation: if we got at least a name, consider it a recommendation
            if course_name != "N/A" or (course_id_or_idea != "N/A" and course_id_or_idea != "New Course Idea"):
                parsed_recommendations.append({
                    "course_id_or_idea": course_id_or_idea,
                    "course_name": course_name,
                    "reasoning": reasoning
                })
            elif block_num == 0 and not parsed_recommendations and not recommendations_output["error_message"] and response_text:
                # If it's the first block, nothing parsed, and no "---" was found, it might be a single malformed rec.
                # Or if the LLM just gives a paragraph without structured fields.
                if len(block.splitlines()) > 1 : # more than one line of text
                    parsed_recommendations.append({
                        "course_id_or_idea": "New Course Idea", # Default if unparseable
                        "course_name": "General AI Suggestion (Unstructured)",
                        "reasoning": block # Use the whole block as reasoning
                    })


        if not parsed_recommendations and not recommendations_output["error_message"]:
            if response_text: # We got some text but couldn't parse it into structured recommendations
                recommendations_output["error_message"] = "AI provided a response, but it could not be parsed into structured recommendations."
            else: # No response text and no earlier error = something went wrong
                recommendations_output["error_message"] = "AI provided no response or an empty response."


        recommendations_output["recommendations"] = parsed_recommendations
        return recommendations_output

    async def decide_leave_request_statuses_for_team(
        self, 
        team_leave_requests: List[Dict], 
        team_id_for_context: Optional[str] = "Unknown Team"
    ) -> List[Dict]:
        """
        Decides on leave request statuses for a team using the Ollama client.
        Input `team_leave_requests`: List of {'id': int, 'reason': str}.
        Return `List[Dict]`, where each dict is {'id': int, 'status': str, 'ai_reasoning': str, 'ai_error_message': Optional[str]}.
        """
        if not team_leave_requests:
            return []

        results_map = {
            req['id']: {
                'id': req['id'], 
                'status': 'error', # Default status
                'ai_reasoning': 'AI processing not initiated.', 
                'ai_error_message': 'AI processing not initiated.'
            } for req in team_leave_requests
        }

        prompt_parts = [
            f"You are an HR operations assistant. For the following leave requests from team '{team_id_for_context}', review each reason and suggest a status ('approved', 'rejected', 'needs discussion') and provide a brief justification (reasoning) for your suggestion for each request ID.",
            "Format your response clearly for each request:",
            "ID: [request_id]",
            "Suggested Status: [status]",
            "Reasoning: [your_reasoning]",
            "---" # Separator
        ]

        for req in team_leave_requests:
            prompt_parts.append(f"ID: {req['id']}\nReason: {req['reason']}\n---")
        
        full_prompt_string = "\n".join(prompt_parts)
        print(f"AIService Leave Decision: Sending prompt to Ollama:\n{full_prompt_string}")

        response_text = None
        try:
            response_text = await self.ollama_client.generate(prompt=full_prompt_string)
            if response_text is None:
                raise ValueError("Ollama client returned None.") # Trigger common error handling
        except Exception as e:
            error_msg = f"Ollama API call failed: {str(e)}"
            print(f"AIService Leave Decision Error: {error_msg}")
            for req_id in results_map:
                results_map[req_id]['ai_reasoning'] = error_msg
                results_map[req_id]['ai_error_message'] = error_msg
            return list(results_map.values())

        print(f"AIService Leave Decision: Received response from Ollama:\n{response_text}")
        
        processed_ids_from_ai = set()
        # Reasoning regex: ([\s\S]+?)(?=ID:|Suggested Status:|Reasoning:|$)
        # This looks for any characters (. including newlines due to \s) lazily (+?)
        # until it hits one of the keywords OR the end of the string ($).
        # This is to prevent reasoning from capturing subsequent fields if they are malformed or missing.
        # However, since we split by "---", each block should be self-contained.
        # So, a simpler regex for reasoning within a block is fine: ([\s\S]+)
        reasoning_regex = r"Reasoning:\s*([\s\S]+)" 

        for block in response_text.split("---"):
            block = block.strip()
            if not block:
                continue

            id_match = re.search(r"ID:\s*(\d+)", block, re.IGNORECASE)
            status_match = re.search(r"Suggested Status:\s*(approved|rejected|needs discussion)", block, re.IGNORECASE)
            # For reasoning, ensure it's the last capture or stop before next field if format is dense
            reasoning_match = re.search(reasoning_regex, block, re.IGNORECASE)
            
            if id_match:
                req_id = int(id_match.group(1))
                processed_ids_from_ai.add(req_id)

                if req_id in results_map:
                    if status_match and reasoning_match:
                        parsed_status = status_match.group(1).lower()
                        parsed_reasoning = reasoning_match.group(1).strip()
                        
                        results_map[req_id]['status'] = parsed_status
                        results_map[req_id]['ai_reasoning'] = parsed_reasoning
                        results_map[req_id]['ai_error_message'] = None
                    else:
                        missing_parts = []
                        if not status_match: missing_parts.append("status")
                        if not reasoning_match: missing_parts.append("reasoning")
                        err_msg = f"Partial data from AI (missing: {', '.join(missing_parts)})."
                        print(f"AIService Leave Decision Warning: For ID {req_id}, {err_msg} Block: '{block[:100]}...'")
                        results_map[req_id]['ai_error_message'] = err_msg
                        # Keep 'status' as 'error' and 'ai_reasoning' as default error message or update with what was parsed
                        if status_match: results_map[req_id]['status'] = status_match.group(1).lower() # if status was parsed but not reasoning
                        if reasoning_match: results_map[req_id]['ai_reasoning'] = reasoning_match.group(1).strip() # if reasoning was parsed but not status
                else:
                    print(f"AIService Leave Decision Warning: AI provided assessment for ID {req_id} not in original request. Ignoring.")
            else:
                print(f"AIService Leave Decision Warning: Could not parse ID from block: '{block[:100]}...'")


        for req_id, result_entry in results_map.items():
            if result_entry['ai_error_message'] == 'AI processing not initiated.' and req_id not in processed_ids_from_ai:
                msg = "AI did not provide assessment for this ID."
                result_entry['ai_error_message'] = msg
                result_entry['ai_reasoning'] = msg
        
        return list(results_map.values())

    async def assess_kpi_results(self, kpi_results_data: List[Dict], user_details: Dict) -> Dict:
        """
        Assesses a list of KPI results for a user using the Ollama client.
        """
        assessment_output = {"assessed_kpis": [], "error_message": None}
        
        # Initialize results with original data to ensure all KPIs are represented
        # This makes it easier to update them with AI assessment or errors later.
        for kpi_data in kpi_results_data:
            assessment_output["assessed_kpis"].append({
                **kpi_data, # Spread original KPI data
                "ai_assessment": "Error: Not processed by AI.",
                "ai_reasoning": "Not processed by AI."
            })

        if not kpi_results_data:
            assessment_output["error_message"] = "No KPI results data provided."
            # Clear the initially added items if input is empty
            assessment_output["assessed_kpis"] = []
            return assessment_output

        # 1. Prompt Construction
        prompt_parts = [
            "You are an expert performance analyst AI. Your task is to assess a list of Key Performance Indicator (KPI) results for a user.",
            "For each KPI result, provide a qualitative Assessment (e.g., 'Exceeds Expectations', 'Meets Expectations', 'Needs Improvement', 'Significantly Below Target') and a brief Reasoning for your assessment based on target vs. actual values and the KPI's nature.",
            "Output each assessment in the following format, ensuring each is separated by '---':",
            "Result ID: [ID of the KPI Result]",
            "Assessment: [Your qualitative assessment]",
            "Reasoning: [Your brief reasoning]",
            "---"
        ]

        prompt_parts.append(f"\nUser Details (for context):")
        prompt_parts.append(f"- User Role: {user_details.get('role', 'N/A')}")
        prompt_parts.append(f"- User Email: {user_details.get('email', 'N/A')}") # Assuming email is available

        prompt_parts.append("\nKPI Results to Assess:")
        for kpi in kpi_results_data:
            prompt_parts.append(
                f"Result ID: {kpi.get('result_id', 'N/A')}\n"
                f"- KPI Name: {kpi.get('kpi_name', 'N/A')}\n"
                f"- KPI Description: {kpi.get('kpi_description', 'N/A')}\n"
                f"- Period: {kpi.get('period', 'N/A')}\n"
                f"- Unit: {kpi.get('unit', 'N/A')}\n"
                f"- Target: {kpi.get('target', 'N/A')}\n"
                f"- Actual Value: {kpi.get('actual_value', 'N/A')}\n"
                # Do not add "---" here, the main instruction specifies it as a separator *between* assessments.
            )
        
        prompt_parts.append("\nBased on the above, provide your assessment for each KPI Result ID:")
        full_prompt_string = "\n".join(prompt_parts)
        # Ensure a final "---" if the AI might not add it after the last item.
        # However, the instruction is for "---" to separate items.
        # Let's rely on the AI to follow the "separated by '---'" for its output blocks.
        
        print(f"AIService KPI Assess: Sending prompt to Ollama:\n{full_prompt_string}")

        # 2. Call Ollama
        response_text = None
        try:
            response_text = await self.ollama_client.generate(prompt=full_prompt_string)
            if response_text is None:
                assessment_output["error_message"] = "Ollama client failed to get a response (returned None)."
                print(f"AIService KPI Assess Error: {assessment_output['error_message']}")
                # All items in assessed_kpis will retain their default error messages
                return assessment_output
        except Exception as e:
            error_msg = f"Error calling Ollama for KPI assessment: {str(e)}"
            assessment_output["error_message"] = error_msg
            print(f"AIService KPI Assess Error: {error_msg}")
            # All items in assessed_kpis will retain their default error messages
            return assessment_output

        # 3. Response Parsing
        print(f"AIService KPI Assess: Received response from Ollama:\n{response_text}")
        
        # Map original kpi_results_data by result_id for easy update
        # This was already done by pre-populating assessment_output["assessed_kpis"]
        
        # Split response into segments for each KPI assessment
        assessment_blocks = [block.strip() for block in response_text.split("---") if block.strip()]

        if not assessment_blocks and response_text:
            assessment_output["error_message"] = "Could not parse assessments from AI response (no valid '---' separators found, or response format incorrect)."
            # All items will retain their default error messages, this is fine.
            return assessment_output
        
        parsed_result_ids = set()

        for block in assessment_blocks:
            result_id_match = re.search(r"Result ID:\s*(\S+)", block, re.IGNORECASE)
            assessment_match = re.search(r"Assessment:\s*(.+)", block, re.IGNORECASE)
            reasoning_match = re.search(r"Reasoning:\s*((?:.|\n)+)", block, re.IGNORECASE) # Multi-line reasoning

            if result_id_match:
                parsed_id_str = result_id_match.group(1).strip()
                try:
                    # Assuming result_id is an integer. Adjust if it's a string.
                    current_result_id = int(parsed_id_str)
                    parsed_result_ids.add(current_result_id)
                except ValueError:
                    print(f"AIService KPI Assess Parse Warning: Found non-integer Result ID '{parsed_id_str}' in response block. Skipping block.")
                    continue # Skip this malformed block

                # Find the corresponding KPI in our pre-populated list
                target_kpi_assessment = next((k for k in assessment_output["assessed_kpis"] if k.get("result_id") == current_result_id), None)
                
                if target_kpi_assessment:
                    if assessment_match:
                        target_kpi_assessment["ai_assessment"] = assessment_match.group(1).strip()
                    else:
                        target_kpi_assessment["ai_assessment"] = "Error: Could not parse Assessment."
                        if not assessment_output["error_message"]: # Set a general error if not already set by Ollama failure
                            assessment_output["error_message"] = "Partial parsing error: Some AI fields could not be extracted."


                    if reasoning_match:
                        raw_reasoning = reasoning_match.group(1).strip()
                        # Clean up reasoning: stop at the next "Result ID:" or "Assessment:" if captured
                        raw_reasoning = re.split(r"\n\s*(?:Result ID:|Assessment:)", raw_reasoning, 1)[0].strip()
                        target_kpi_assessment["ai_reasoning"] = raw_reasoning if raw_reasoning else "Reasoning provided but was empty."
                    else:
                        target_kpi_assessment["ai_reasoning"] = "Error: Could not parse Reasoning."
                        if not assessment_output["error_message"]:
                            assessment_output["error_message"] = "Partial parsing error: Some AI fields could not be extracted."
                else:
                    print(f"AIService KPI Assess Parse Warning: AI provided assessment for Result ID {current_result_id} not in original request. Ignoring.")
            else:
                print(f"AIService KPI Assess Parse Warning: Found a block without a parseable 'Result ID:'. Block content: '{block[:100]}...'")


        # Check if any original KPIs were not mentioned by the AI
        for kpi_assessment in assessment_output["assessed_kpis"]:
            if kpi_assessment.get("result_id") not in parsed_result_ids and kpi_assessment.get("ai_assessment") == "Error: Not processed by AI.":
                kpi_assessment["ai_reasoning"] = "AI response did not include an assessment for this KPI."
                if not assessment_output["error_message"]:
                     assessment_output["error_message"] = "Partial processing: AI did not provide assessments for all KPIs."


        if not parsed_result_ids and not assessment_output["error_message"] and response_text:
            assessment_output["error_message"] = "AI provided a response, but no Result IDs could be parsed. Assessments not applied."
        elif not parsed_result_ids and not assessment_output["error_message"] and not response_text:
             assessment_output["error_message"] = "AI provided no response or an empty response."


        return assessment_output
