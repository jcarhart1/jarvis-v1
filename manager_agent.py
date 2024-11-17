import asyncio  # Asynchronous programming support
from tools import connect_to_database, run_query, close_connection, search_web, start_rag_app  # Import necessary tools
from llm_config import query_llm  # Import function to query the LLM


async def manager_agent():
    """
    Main function for the Manager Agent. This agent listens for user commands, analyzes them,
    and decides on the appropriate action using an LLM with reasoning capabilities.

    The agent can:
    - Perform web searches
    - Connect to a database and run queries
    - Start a RAG application for internal document processing

    Instructions and examples are provided to the LLM to ensure accurate action selection.
    """
    print("Manager Agent with ReAct capabilities started. Type your command or 'exit' to stop.")

    while True:
        # Accept user input
        user_prompt = input("You: ")

        # Exit the loop if the user types 'exit'
        if user_prompt.lower() == 'exit':
            print("Exiting Manager Agent.")
            break

        # Check if the command directly mentions "RAG" or "internal docs" and start RAG if so
        if "rag" in user_prompt.lower() or "internal docs" in user_prompt.lower():
            print("Starting the RAG application for internal document processing...")
            start_rag_app()
            continue  # Skip the LLM query as action is already determined

        # Formulate the LLM prompt to guide it toward correct actions
        prompt = f"""
        You are an intelligent assistant capable of reasoning and taking actions. Please reason before
        taking any action and provide the best response based on the user's request.

        Available actions:
        - search_web(query): Perform a web search
        - connect_to_database(): Connect to the database
        - start_rag_app(): Start the RAG application for internal document processing

        Rules:
        - If the user's request includes "RAG" or "internal docs", always respond with "Action: start_rag_app()".
        - If the user's request includes "run query", respond with "Action: connect_to_database()".
        - For other general questions or requests, decide the best action.
        - Remember what you have learned from previous interactions in case the user asks follow up questions.

        Examples:
        - User request: "Search for machine learning updates"
          Response: Action: search_web("machine learning updates")

        - User request: "Research the association between dietary iron and type two diabetes"
          Response: Action: search_web("iron and type two diabetes association")

        - User request: "Connect to my database"
          Response: Action: connect_to_database()

        - User request: "Run a query"
          Response: Action: connect_to_database()

        - User request: "Use RAG on internal docs"
          Response: Action: start_rag_app()

        User request: "{user_prompt}"
        Remember, respond only with the action in the format: Action: <action_name>.
        """

        # Query the LLM with the formulated prompt
        response = query_llm(prompt)

        if response:
            print(f"LLM Response:\n{response}")

            # Parse the response to find the specified action
            if "Action:" in response:
                # Extract the action line and determine the action type
                action_line = response.split("Action:")[-1].strip()

                # Check if the action is a web search
                if "search_web(" in action_line:
                    # Extract query from the response
                    query = action_line.split("(")[1].split(")")[0].strip('"')
                    print(f"Performing web search for: {query}")
                    results = search_web(query)

                    # Display search results
                    if results:
                        print(f"Data retrieved: {len(results)} hits.")
                        for idx, result in enumerate(results, start=1):
                            print(f"{idx}. {result['title']} - {result['link']}")
                    else:
                        print("No results found.")

                # Check if the action is to connect to the database
                elif "connect_to_database" in action_line:
                    print("Connecting to the database...")
                    conn = connect_to_database()

                    if conn:
                        # Prompt user for an SQL query if database connection is successful
                        query = input("Please enter the SQL query you would like to run:\n")
                        run_query(conn, query)  # Execute the user-specified query
                        close_connection(conn)  # Close the connection afterward
                    else:
                        print("Failed to establish a database connection.")

                # Check if the action is to start the RAG application
                elif "start_rag_app" in action_line:
                    print("Starting the RAG application...")
                    start_rag_app()  # Run the RAG application for internal document processing

                else:
                    # If no recognizable action was found, log a message
                    print("No recognizable action found in the response.")
            else:
                # Handle cases where no action is detected in the LLM's response
                print("No action detected in LLM response.")
        else:
            # If the LLM response is None or empty, log an error message
            print("Failed to get a response from the LLM.")


# Entry point for running the manager agent asynchronously
if __name__ == "__main__":
    asyncio.run(manager_agent())
