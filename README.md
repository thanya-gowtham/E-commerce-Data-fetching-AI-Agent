# 📦 E-commerce Data-Fetching AI Agent

A local AI-powered agent built with *LangChain, **Mistral (via Ollama), and **SQLite, enabling users to ask **natural language questions* about their e-commerce data and get answers in plain text, charts, or markdown — all in a local, privacy-friendly setup.

---

## 🔍 Features

- 💬 Ask questions like:
  - "Show total sales for June"
  - "Which category sold most in Q1?"
  - "Plot weekly revenue for each brand"

- ⚡ Powered by [Ollama](https://ollama.com) running *Mistral* locally
- 📊 Automatically generates *SQL, **markdown tables, and **charts*
- 🧠 Uses *LangChain’s SQL Agent*
- 🗃 Works with any structured CSV data loaded into SQLite
- 🌐 Built-in frontend with real-time streaming UI

---

## 🚀 Getting Started

### 1. Steps

```bash
git clone https://github.com/achugowda/E-commerce-Data-fetching-AI-Agent.git
cd E-commerce-Data-fetching-AI-Agent

### 2. Create and Activate Virtual Environment
python -m venv venv

# For Linux/Mac
source venv/bin/activate

# For Windows
venv\Scripts\activate

### 3. Install Python Dependencies
pip install -r requirements.txt

### 4. Set Up Ollama and Pull Mistral Model

Download and install Ollama from: https://ollama.com
Open a terminal and pull the Mistral model:
ollama pull mistral
Make sure Ollama is running in the background.

## How It Works

database.py – Loads your ecommerce .csv into SQLite.
llm_agent.py – Runs LangChain’s SQL Agent over your database.
main.py – FastAPI backend to serve user queries.
frontend/ – Web UI to input queries and see results in real-time (with markdown + charts).


##📂 Folder Structure

E-commerce-Data-fetching-AI-Agent/
├── database.py
├── llm_agent.py
├── main.py
├── requirements.txt
├── frontend/
│   ├── index.html
│   └── ...
└── data/
    └── ecommerce.csv  ← (Your data file)
