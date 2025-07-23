from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain.agents import AgentExecutor, initialize_agent, AgentType
from langchain_community.utilities import SQLDatabase
from langchain_community.llms import Ollama
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import warnings
import asyncio

# Suppress LangChain agent deprecation warning
warnings.filterwarnings("ignore", category=UserWarning)

# ✅ Step 1: Custom system prompt for markdown tables
system_prompt = """You are an intelligent data analyst.
When presenting tabular data like grouped sales, averages, or comparisons, always format it using Markdown tables (pipe | separated).
Avoid unnecessary explanations. Keep answers clean, brief, and formatted as tables wherever applicable."""

# ✅ Step 2: Setup LLM with prompt (llama3)
llm = Ollama(model="llama3", temperature=0.2)

# ✅ Step 3: Connect to DB and setup toolkit
db = SQLDatabase.from_uri("sqlite:///ecommerce.db")
toolkit = SQLDatabaseToolkit(db=db, llm=llm)

# ✅ Step 4: Initialize agent with system message
agent_executor = initialize_agent(
    tools=toolkit.get_tools(),
    llm=llm,
    agent=AgentType.OPENAI_FUNCTIONS,
    verbose=True,
    agent_kwargs={
        "system_message": system_prompt
    }
)

# ✅ Step 5: Async agent function to query from Streamlit frontend
async def query_data_agent(query: str) -> str:
    try:
        result = await agent_executor.ainvoke({"input": query})
        return result["output"]
    except Exception as e:
        return f"❌ Error: {e}"

# ✅ (Optional) Run sample queries if executed directly
if __name__ == "__main__":
    async def run_queries():
        print("\n--- Testing LLM Agent ---\n")
        queries = [
            "Show the total sales amount grouped by product category.",
            "List the average sales per item per category.",
        ]
        for q in queries:
            print(f"\n🟡 Query: {q}")
            res = await query_data_agent(q)
            print(f"✅ Response:\n{res}\n")

    asyncio.run(run_queries())