import streamlit as st
import requests
import json
import plotly.graph_objects as go
import pandas as pd
from io import StringIO

# --- Configuration ---
BACKEND_URL = "http://127.0.0.1:8000" # Ensure this matches your FastAPI server address

st.set_page_config(page_title="E-commerce AI Data Agent", layout="wide")

st.title("🛍️ E-commerce AI Data Agent")
st.markdown("Ask me anything about your e-commerce sales, ads, or product eligibility data!")

# --- Chat History Management ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "plot_data" in message and message["plot_data"]:
            fig = go.Figure(message["plot_data"])
            st.plotly_chart(fig, use_container_width=True)
        if "table_data" in message and message["table_data"]:
            st.dataframe(pd.DataFrame(message["table_data"]), use_container_width=True)

# --- User Input and Query Submission ---
if prompt := st.chat_input("Ask a question..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        plot_data = None
        table_data = None

        try:
            # Use the streaming endpoint for a live typing effect
            with requests.get(f"{BACKEND_URL}/stream_query", params={"question": prompt}, stream=True) as r:
                r.raise_for_status() # Raise an exception for HTTP errors
                for chunk in r.iter_content(chunk_size=None): # Process chunks as they arrive
                    if chunk:
                        # SSE messages are prefixed with "data: " and end with "\n\n"
                        decoded_chunk = chunk.decode('utf-8')
                        if decoded_chunk.startswith("data: "):
                            try:
                                event_data = json.loads(decoded_chunk[len("data: "):].strip())
                                if event_data.get("type") == "text":
                                    full_response += event_data.get("content", "")
                                    message_placeholder.markdown(full_response + "▌") # Add blinking cursor
                                elif event_data.get("type") == "end":
                                    # End of stream, now fetch the full structured response for plot/table data
                                    # This is a workaround; ideally, streaming would include structured data
                                    response = requests.post(f"{BACKEND_URL}/query", params={"question": prompt}).json()
                                    full_response = response.get("answer", "No answer received.")
                                    plot_data = response.get("plot_data")
                                    table_data = response.get("table_data")
                                    break # Exit streaming loop
                            except json.JSONDecodeError:
                                # Handle cases where chunk is not a complete JSON object
                                pass
            
            message_placeholder.markdown(full_response) # Display final text response

            if plot_data:
                fig = go.Figure(plot_data)
                st.plotly_chart(fig, use_container_width=True)
            if table_data:
                st.dataframe(pd.DataFrame(table_data), use_container_width=True)

            st.session_state.messages.append({
                "role": "assistant",
                "content": full_response,
                "plot_data": plot_data,
                "table_data": table_data
            })

        except requests.exceptions.ConnectionError:
            st.error("Could not connect to the backend API. Please ensure FastAPI server is running.")
            st.session_state.messages.append({"role": "assistant", "content": "Error: Could not connect to the backend API."})
        except requests.exceptions.RequestException as e:
            st.error(f"An error occurred: {e}")
            st.session_state.messages.append({"role": "assistant", "content": f"Error: {e}"})