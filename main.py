# main.py
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json
import plotly.express as px
import pandas as pd
from io import StringIO
from sqlalchemy import text

# Import our LLM agent and database setup
from llm_agent import query_data_agent
from database import load_data_to_db, get_db_schema, engine # Import engine for direct query if needed

app = FastAPI(
    title="E-commerce AI Agent API",
    description="API for querying e-commerce data using an AI agent.",
    version="1.0.0"
)

# Configure CORS to allow requests from your Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Adjust this to your Streamlit app's URL in production (e.g., "http://localhost:8501")
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Data Loading on Startup ---
@app.on_event("startup")
async def startup_event():
    print("Loading data into database on startup...")
    load_data_to_db()
    print("Database ready.")

# --- API Endpoint for NL Query ---
@app.post("/query")
async def query_ecommerce_data(question: str):
    """
    Receives a natural language question and returns an answer,
    potentially with a visualization.
    """
    print(f"Received query: {question}")

    # Use the LLM agent to get the response
    # The agent's response might contain text and/or data for visualization
    agent_response = await query_data_agent(question)

    # Attempt to parse the agent's response for potential SQL query and results
    # This is a simplified parsing; a more robust solution would involve structured output from the LLM
    
    # Check if the response contains a DataFrame string for visualization
    df_str_prefix = "```dataframe\n"
    if df_str_prefix in agent_response:
        try:
            # Extract the DataFrame string
            df_start = agent_response.find(df_str_prefix) + len(df_str_prefix)
            df_end = agent_response.find("\n```", df_start)
            df_csv_str = agent_response[df_start:df_end].strip()
            
            # Extract the textual part of the response
            text_response = agent_response[:df_start - len(df_str_prefix)].strip() + agent_response[df_end + 4:].strip()

            # Read the CSV string into a pandas DataFrame
            df = pd.read_csv(StringIO(df_csv_str))

            # Generate a Plotly chart (example: bar chart for simple data)
            # This logic needs to be smarter based on the query type
            fig_json = None
            if not df.empty:
                # Simple heuristic for visualization: if two columns, try bar chart
                if len(df.columns) == 2:
                    # Assuming first column is categorical, second is numerical
                    fig = px.bar(df, x=df.columns, y=df.columns[1], title=f"Results for '{question}'")
                    fig_json = fig.to_json()
                elif len(df.columns) > 0:
                    # For more complex data, just return the table for now
                    pass # Or implement more sophisticated chart selection

            return JSONResponse(content={
                "answer": text_response,
                "plot_data": json.loads(fig_json) if fig_json else None,
                "table_data": df.to_dict(orient='records') if not df.empty else None
            })

        except Exception as e:
            print(f"Error processing visualization data: {e}")
            # Fallback to just text response if visualization fails
            return JSONResponse(content={"answer": agent_response, "plot_data": None, "table_data": None})
    
    # If no DataFrame string, return plain text response
    return JSONResponse(content={"answer": agent_response, "plot_data": None, "table_data": None})

# --- Streaming Endpoint (for live typing effect) ---
@app.get("/stream_query")
async def stream_query_ecommerce_data(question: str):
    """
    Receives a natural language question and streams the LLM's response
    token by token.
    """
    print(f"Received streaming query: {question}")

    async def event_generator():
        # This part needs modification in llm_agent.py to support streaming directly from Ollama/LangChain
        # For now, we'll simulate streaming a pre-generated response or the full response
        # LangChain's.astream() method would be used here if the agent supported it directly.
        # As a workaround, we'll get the full response and stream it character by character.
        full_response = await query_data_agent(question)
        
        for char in full_response:
            yield f"data: {json.dumps({'type': 'text', 'content': char})}\n\n"
            await asyncio.sleep(0.02) # Simulate typing delay

        # After text, send any plot data if available (this would require agent_response to be structured)
        # For simplicity, this example only streams text.
        # A more advanced implementation would have the LLM output structured JSON for text and plot data.
        yield f"data: {json.dumps({'type': 'end'})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

# --- Health Check Endpoint ---
@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "E-commerce AI Agent API is running."}

# --- Example of direct SQL execution (for debugging/testing) ---
@app.post("/execute_sql")
async def execute_sql_query(sql_query: str):
    """Executes a raw SQL query against the database."""
    try:
        with engine.connect() as connection:
            result = connection.execute(text(sql_query))
            # For SELECT queries, fetch results
            if sql_query.strip().upper().startswith("SELECT"):
                columns = result.keys()
                rows = result.fetchall()
                data = [dict(zip(columns, row)) for row in rows]
                return JSONResponse(content={"status": "success", "data": data})
            else:
                connection.commit() # Commit for DML operations
                return JSONResponse(content={"status": "success", "message": "SQL command executed."})
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"SQL execution error: {e}")