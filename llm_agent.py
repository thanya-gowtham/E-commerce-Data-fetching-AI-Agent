from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.llms.ollama import Ollama
from langchain.agents.agent_toolkits.sql.base import create_sql_agent
from sqlalchemy import create_engine, inspect
import os

# Step 1: Database setup
DATABASE_URL = "sqlite:///./ecommerce.db"
engine = create_engine(DATABASE_URL)
db = SQLDatabase(engine)

# Step 2: LLM setup
llm = Ollama(model="gemma:2b", temperature=0)

# Step 3: Toolkit setup
toolkit = SQLDatabaseToolkit(db=db, llm=llm)

# Step 4: Create agent
agent_executor = create_sql_agent(
    llm=llm,
    toolkit=toolkit,
    verbose=True,
    handle_parsing_errors=True
)

async def query_data_agent(question: str):
    """Query the database using the LangChain SQL agent."""
    try:
        response = await agent_executor.ainvoke({"input": question})
        return response.get("output", "Could not retrieve an answer.")
    except Exception as e:
        print(f"Error in LLM agent: {e}")
        return f"An error occurred: {e}"

# Testing
if __name__ == "__main__":
    import asyncio
    from database import load_data_to_db

    load_data_to_db()

    async def run_tests():
        print("\n--- Testing LLM Agent ---")

        queries = [
            "What is  total sales for item id 17"
        ]

        for q in queries:
            print(f"\nQuery: {q}")
            res = await query_data_agent(q)
            print(f"Response: {res}")

    asyncio.run(run_tests())
