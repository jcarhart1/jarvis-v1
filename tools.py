import requests  # For making HTTP requests to the web search API
import os  # For accessing environment variables
import pandas as pd  # For handling and displaying SQL results in a table
from tabulate import tabulate  # Optional: used for formatted table output
from sqlalchemy import create_engine  # For connecting to the database via SQLAlchemy
import subprocess  # For starting external processes like the RAG application
from dotenv import load_dotenv  # For loading environment variables from a .env file
import time  # For introducing delays during process monitoring
import logging  # For logging events and debugging information

# Load environment variables from a .env file in the project root
load_dotenv(".env")

# Load API key for web search from environment variables
SERPAPI_KEY = os.getenv("SERPAPI_KEY")  # SerpAPI key needed for web search functionality

# Set up logging to capture debug-level information
logging.basicConfig(level=logging.DEBUG)


# --- Database Connection Tool ---
def connect_to_database():
    """
    Establishes a connection to a PostgreSQL database using SQLAlchemy and returns an engine object.

    Returns:
        engine (SQLAlchemy Engine): Connection to the database or None if the connection fails.
    """
    try:
        # Database connection URL, constructed from environment variables
        db_url = f"postgresql+psycopg2://{os.getenv('DB_USER')}:" \
                 f"{os.getenv('DB_PASSWORD')}@" \
                 f"{os.getenv('DB_HOST')}/" \
                 f"{os.getenv('DB_NAME')}"

        # Create an SQLAlchemy engine for database interaction
        engine = create_engine(db_url)
        logging.info("Connected to the database.")
        return engine
    except Exception as e:
        logging.error(f"Failed to connect to the database: {e}")
        return None


def run_query(conn, query):
    """
    Executes a SQL query on the database and saves the results to an HTML file for easy review.

    Args:
        conn (SQLAlchemy Engine): The active database connection.
        query (str): SQL query string to be executed.

    Side Effect:
        Creates an HTML file 'query_results.html' containing the query results.
    """
    try:
        # Execute the SQL query and load results into a DataFrame
        df = pd.read_sql_query(query, conn)

        # Save the DataFrame to an HTML file for a human-readable format
        output_path = "query_results.html"
        df.to_html(output_path, index=False)
        logging.info(f"Query results saved to {output_path}")

    except Exception as e:
        logging.error(f"Error executing query: {e}")


def close_connection(engine):
    """
    Disposes of the SQLAlchemy engine, effectively closing the database connection.

    Args:
        engine (SQLAlchemy Engine): The database connection engine to close.
    """
    if engine:
        engine.dispose()  # Properly closes the SQLAlchemy engine
        logging.info("Database connection closed.")


# --- Web Search Tool ---
def search_web(query):
    """
    Conducts a web search using SerpAPI and returns a list of results.

    Args:
        query (str): Search term or question to query on Google via SerpAPI.

    Returns:
        list: A list of dictionaries with 'title' and 'link' keys for each result.
    """
    logging.info("Connecting to Google for web search...")

    # Parameters for the SerpAPI search, including API key and search engine type
    params = {
        "engine": "google",
        "q": query,
        "api_key": SERPAPI_KEY,
        "num": 10  # Number of results to fetch
    }

    # Perform the web search request
    response = requests.get("https://serpapi.com/search", params=params)
    if response.status_code == 200:
        data = response.json()
        search_results = data.get("organic_results", [])
        if search_results:
            logging.info(f"Found {len(search_results)} results.")
            return [{"title": result["title"], "link": result["link"]} for result in search_results]
        else:
            logging.info("No search results found.")
            return []
    else:
        logging.error(f"Error fetching search results: {response.status_code}")
        return []


# --- RAG Application Tool ---
def start_rag_app():
    """
    Starts the RAG application by running two scripts: serve.py (for server setup) and terminal_q_and_a.py
    (for handling queries). This function monitors the output and logs the startup status of each script.
    """
    try:
        logging.info("Starting the RAG application...")

        # Start serve.py directly, which is expected to set up the application server
        logging.info("Starting serve.py...")
        serve_process = subprocess.Popen(["python", "serve.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Timeout loop to monitor serve.py startup and check for expected output message
        timeout = 10  # Maximum wait time (in seconds) for serve.py to start
        start_time = time.time()

        logging.info("Waiting for serve.py to start...")
        while time.time() - start_time < timeout:
            line = serve_process.stdout.readline().decode().strip()
            if line:
                logging.debug(f"serve.py output: {line}")
            if line and "Expected startup message" in line:  # Replace with actual expected message if available
                logging.info("serve.py started successfully.")
                break
            time.sleep(1)

        # Start terminal_q_and_a.py directly, which processes user queries against RAG data
        logging.info("Starting terminal_q_and_a.py...")
        app_process = subprocess.Popen(["python", "terminal_q_and_a.py"], stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE)

        # Monitor terminal_q_and_a.py output for any immediate feedback
        for line in app_process.stdout:
            logging.debug(f"terminal_q_and_a.py output: {line.decode().strip()}")

        # Log errors from stderr of both processes for debugging and monitoring
        for line in serve_process.stderr:
            logging.error(f"serve.py error: {line.decode().strip()}")

        for line in app_process.stderr:
            logging.error(f"terminal_q_and_a.py error: {line.decode().strip()}")

    except Exception as e:
        logging.error(f"Failed to start RAG application: {e}")
