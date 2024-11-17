import os  # For accessing environment variables
import json  # For handling JSON data
import logging  # For debugging and tracking errors/events
from dotenv import load_dotenv  # For loading environment variables from a .env file
import requests  # For making HTTP requests to the API

# Load environment variables from a .env file located in the same directory
load_dotenv(".env")

# Retrieve API key for Grok from environment variables
GROK_API_KEY = os.getenv("GROK_API_KEY")  # Must be set in .env file
url = "https://api.groq.com/openai/v1/chat/completions"  # API endpoint for chat-based completions

# Enable detailed logging for debugging purposes
logging.basicConfig(level=logging.DEBUG)


def query_llm(prompt):
    """
    Sends a prompt to the Large Language Model (LLM) via the Grok API and returns the response.

    Args:
        prompt (str): The user input or question to be processed by the LLM.

    Returns:
        str or None: The response text from the LLM if successful; otherwise, None.
    """

    # HTTP headers required for making an authenticated API request
    headers = {
        "Authorization": f"Bearer {GROK_API_KEY}",  # API authentication
        "Content-Type": "application/json"  # Specifies JSON format
    }

    # Payload structure sent to the API, containing model details and user prompt
    payload = {
        "model": "llama3-70b-8192",  # Model name/version specified by the API
        "messages": [{"role": "user", "content": prompt}],  # Chat-style format; "user" as role
        "max_tokens": 150,  # Limits response length to manage token usage
        "temperature": 0.7,  # Adjusts creativity/randomness of responses
        "stop": ["\n", "User:"]  # Sequences that terminate the response early
    }

    # Logs the payload for debugging, showing data sent to the API
    logging.debug(f"Payload: {json.dumps(payload)}")

    # Send the request and handle potential errors
    try:
        # Makes the POST request to the API endpoint
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()  # Raises HTTPError for unsuccessful requests

        # Converts response to JSON for easy processing and logs it
        response_json = response.json()
        logging.debug(f"Response JSON: {json.dumps(response_json, indent=2)}")

        # Parse response content for the generated text
        if "choices" in response_json and response_json["choices"]:
            # Selects the first choice in the response list
            choice = response_json["choices"][0]
            # Attempt to retrieve text from "choices" with different possible formats
            if "text" in choice:
                return choice["text"].strip()  # Standard text format
            elif "message" in choice and "content" in choice["message"]:
                return choice["message"]["content"].strip()  # Chat-like format
            else:
                # Logs an error if neither expected format is found in the response
                logging.error("Unexpected response format in 'choices'. No 'text' or 'message' found.")
        else:
            # Logs an error if 'choices' field is missing or empty
            logging.error("No 'choices' field found in response JSON.")

    except requests.exceptions.HTTPError as http_err:
        # Logs HTTP-specific errors, providing status and content for troubleshooting
        logging.error(f"HTTP error: {http_err}")
        logging.error(f"Response content: {response.text}")
    except Exception as err:
        # Logs any other types of errors encountered
        logging.error(f"Other error occurred: {err}")

    return None  # Returns None if response parsing fails or an error occurs
