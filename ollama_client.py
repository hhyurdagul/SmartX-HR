# ollama_client.py
# This module provides a client for interacting with the Ollama API.

# Configuration options:
# - OLLAMA_API_URL: Overrides the default API URL (http://localhost:11434/api/generate).
# - OLLAMA_DEFAULT_MODEL: Overrides the default model name (e.g., mistral).

import json
import os
import requests
import asyncio # Added asyncio

DEFAULT_OLLAMA_API_URL = "http://localhost:11434/api/generate"
DEFAULT_OLLAMA_MODEL = "mistral"

class OllamaClient:
    def __init__(self, api_url=None, model=None):
        self.api_url = os.environ.get("OLLAMA_API_URL", api_url or DEFAULT_OLLAMA_API_URL)
        self.model = os.environ.get("OLLAMA_DEFAULT_MODEL", model or DEFAULT_OLLAMA_MODEL)

    async def generate(self, prompt, model=None, api_url=None): # Changed to async def
        """
        Generates text using the Ollama API.

        Args:
            prompt (str): The prompt to send to the API.
            model (str, optional): The model to use. Defaults to the client's configured model.
            api_url (str, optional): The API URL to use. Defaults to the client's configured API URL.

        Returns:
            str: The generated text, or None if an error occurred.
        """
        current_api_url = api_url or self.api_url
        current_model = model or self.model

        payload = {
            "model": current_model,
            "prompt": prompt,
            "stream": False,
        }

        def _post_and_parse_sync():
            # This synchronous function will be run in a separate thread
            res = requests.post(current_api_url, json=payload, timeout=10) # Added timeout
            res.raise_for_status()  # Raise an exception for bad status codes
            return res.json()

        try:
            response_json = await asyncio.to_thread(_post_and_parse_sync)
            return response_json.get("response")
        except requests.exceptions.RequestException as e:
            print(f"Error connecting to Ollama API: {e}")
            return None
        except json.JSONDecodeError as e: # Should be less likely if _post_and_parse_sync handles it
            print(f"Error parsing JSON response from Ollama API: {e}")
            return None
        except Exception as e: # Catch any other unexpected errors from to_thread or elsewhere
            print(f"An unexpected error occurred: {e}")
            return None

# Example Usage:
# if __name__ == "__main__":
#     client = OllamaClient()
#
#     async def main(): # Define an async main function
#         # Example 1: Use default model and API URL
#         prompt1 = "What is the capital of France?"
#         response1 = await client.generate(prompt1) # Use await
#         if response1:
#             print(f"Prompt: {prompt1}")
#             print(f"Response: {response1}")
#
#         # Example 2: Override model
#         prompt2 = "Explain quantum computing in simple terms."
#         response2 = await client.generate(prompt2, model="llama2") # Use await
#         if response2:
#             print(f"\nPrompt: {prompt2}")
#             print(f"Response: {response2}")
#
#         # Example 3: Override API URL (if you have another instance running)
#         # prompt3 = "Tell me a joke."
#         # response3 = await client.generate(prompt3, api_url="http://localhost:11435/api/generate") # Use await
#         # if response3:
#         #     print(f"\nPrompt: {prompt3}")
#         #     print(f"Response: {response3}")
#
#         # Example 4: Non-existent model or API
#         prompt4 = "This should fail."
#         response4 = await client.generate(prompt4, model="non_existent_model") # Use await
#         if not response4:
#             print(f"\nFailed to get response for prompt: {prompt4} (as expected)")
#
#         response5 = await client.generate(prompt4, api_url="http://localhost:12345/api/generate") # Use await
#         if not response5:
#             print(f"Failed to get response for prompt: {prompt4} with invalid API (as expected)")
#
#     asyncio.run(main()) # Run the async main function
