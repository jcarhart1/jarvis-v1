import os
import json
import logging
from dotenv import load_dotenv
import requests
from groq import Groq

load_dotenv(".env")

# GROK_API_KEY = os.getenv("GROK_API_KEY")  # Set your Grok API key here

GROK_API_KEY='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'
url = "https://api.groq.com/openai/v1/chat/completions"

# Enable logging
logging.basicConfig(level=logging.DEBUG)


def query_llm(prompt):
    """
    Sends a prompt to the LLM via the Grok API and returns the response.
    """
    headers = {
        "Authorization": f"Bearer {GROK_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "llama3-70b-8192",  # Ensure the model field is correct
        "messages": [{"role": "user", "content": prompt}],  # Assuming the API expects a chat-like format
        "max_tokens": 150,
        "temperature": 0.7,
        "stop": ["\n", "User:"]
    }

    # Debugging information for payload
    logging.debug(f"Payload: {json.dumps(payload)}")

    # Send the request
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()  # Raise an HTTPError for bad requests

        # Debugging information for response JSON structure
        response_json = response.json()
        logging.debug(f"Response JSON: {json.dumps(response_json, indent=2)}")

        # Attempt to extract text content based on possible response formats
        if "choices" in response_json and response_json["choices"]:
            choice = response_json["choices"][0]
            # Check for text under different possible keys
            if "text" in choice:
                return choice["text"].strip()
            elif "message" in choice and "content" in choice["message"]:
                return choice["message"]["content"].strip()
            else:
                logging.error("Unexpected response format in 'choices'. No 'text' or 'message' found.")
        else:
            logging.error("No 'choices' field found in response JSON.")

    except requests.exceptions.HTTPError as http_err:
        logging.error(f"HTTP error: {http_err}")
        logging.error(f"Response content: {response.text}")
    except Exception as err:
        logging.error(f"Other error occurred: {err}")
    return None