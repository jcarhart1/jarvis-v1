import requests
import os
import psycopg2  # For database connection

# --- Database Connection Agent ---
def connect_to_database():
    """
    Connects to the PostgreSQL database and returns a connection object.
    """
    try:
        # Define connection parameters
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST', 'postgres-db-dev.c7sosyk2g2tx.us-east-1.rds.amazonaws.com'),
            database=os.getenv('DB_NAME', 'cms'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', 'Pebtf#1#GriffClem')  # Set this in your environment variables
        )
        print("Connected to the database.")
        return conn
    except Exception as e:
        print(f"Failed to connect to the database: {e}")
        return None

def run_query(conn, query):
    """
    Runs a SQL query on the connected database and returns the results.
    """
    try:
        with conn.cursor() as cursor:
            cursor.execute(query)
            results = cursor.fetchall()
            for row in results:
                print(row)
    except Exception as e:
        print(f"Error executing query: {e}")

def close_connection(conn):
    """
    Closes the connection to the database.
    """
    if conn:
        conn.close()
        print("Database connection closed.")


# --- Web Search Agent ---
SERPAPI_KEY = "0b7993739584a9776dc60980f6beb5ba017207905db7ca7e3054a35070461d93"

def search_web(query):
    """
    Perform a web search using SerpAPI and return search results.
    """
    print("Connecting to Google...")

    params = {
        "engine": "google",
        "q": query,
        "api_key": SERPAPI_KEY,
        "num": 10
    }

    response = requests.get("https://serpapi.com/search", params=params)
    if response.status_code == 200:
        data = response.json()
        search_results = data.get("organic_results", [])
        if search_results:
            print(f"Found {len(search_results)} results.")
            return [{"title": result["title"], "link": result["link"]} for result in search_results]
        else:
            return []
    else:
        print("Error: Unable to fetch results.")
        return []
