import streamlit as st
import asyncio
from llm_agent import query_data_agent  # Assuming llm_agent.py is in the same directory
import matplotlib.pyplot as plt
import pandas as pd
import re

st.set_page_config(page_title="E-Commerce AI Agent", layout="centered")
st.title("🛍️ E-Commerce Data Query Agent")

user_query = st.text_input("Enter your natural language query:")

if st.button("Run Query") and user_query:
    with st.spinner("Thinking..."):

        # Run the async agent function
        response = asyncio.run(query_data_agent(user_query))
        st.success("Response received!")

        # ✅ STREAM THE RESPONSE
        import time
        st.markdown("### 🔍 Live Agent Response:")
        for chunk in response.split(". "):  # simple sentence splitter
            st.write(chunk.strip() + ("" if chunk.endswith(".") else "."))
            time.sleep(0.5)

        # 📊 Optional: Plot if the response contains table data
        if "|" in response:
            rows = [line.strip() for line in response.splitlines() if "|" in line and not line.startswith("|--")]
            if len(rows) > 1:
                headers = [col.strip() for col in rows[0].split("|") if col]
                data = [[cell.strip() for cell in row.split("|") if cell] for row in rows[1:]]
                df = pd.DataFrame(data, columns=headers)
                df[headers[1]] = pd.to_numeric(df[headers[1]], errors="coerce")
                st.bar_chart(df.set_index(headers[0]))