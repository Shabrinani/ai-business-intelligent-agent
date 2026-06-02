# AI Business Intelligence Agent

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.57.0-FF4B4B.svg?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![LangChain](https://img.shields.io/badge/LangChain-1.3.1-1C3C3C.svg)](https://python.langchain.com/)
[![LangChain Groq](https://img.shields.io/badge/LangChain_Groq-1.1.2-f55036.svg)](https://groq.com/)
[![Pandas](https://img.shields.io/badge/Pandas-3.0.3-150458.svg?logo=pandas&logoColor=white)](https://pandas.pydata.org/)
[![DuckDuckGo Search](https://img.shields.io/badge/DuckDuckGo_Search-8.1.1-DE5833.svg)](https://pypi.org/project/duckduckgo-search/)

An autonomous, LLM-powered Business Intelligence application built with Streamlit and LangChain. This agent allows users to interact with their tabular data (CSV) using natural language, generate visual charts dynamically, and search the web for real-time business context.

Access the app here: [credit-default-prediction-app.streamlit.app](https://ai-business-intelligent-agent.streamlit.app/)

https://github.com/user-attachments/assets/602e99cd-e902-41ac-9825-465d0b8c2691

---

## Key Features

* **Conversational Data Analysis:** Chat with your dataset to extract exact numbers, trends, and summaries without writing a single line of SQL or Python.
* **Autonomous Visualization:** Ask the agent to draw a chart, and it will dynamically generate Python code (using `matplotlib`/`seaborn`), execute it, and render the plot directly in the chat interface.
* **Real-time Web Search Integration:** Equipped with a DuckDuckGo search tool to pull external, real-time market context that isn't available in the uploaded dataset.
* **Smart Data Profiling:** Automatically displays dataset metadata, including total rows, columns, data types, and null value counts upon file upload.

## System Architecture

The core of this application is a LangChain `create_agent` orchestrator equipped with three distinct tools:
1.  `Data_Analyzer_Tool`: Utilizes LangChain's `create_pandas_dataframe_agent` to evaluate natural language queries against the active Pandas DataFrame.
2.  `Visualization_Tool`: A highly optimized prompt engine that generates and saves `seaborn`/`matplotlib` plots as unique image files, preventing Streamlit media storage crashes.
3.  `Internet_Search_Tool`: A fallback tool for external intelligence gathering, wrapped in an anti-bot exception handler.

## Challenges & Known Limitations

Building this autonomous agent required handling several real-world edge cases:

* **API Rate Limits & Prompt Optimization:** The `pandas_dataframe_agent` requires injecting the dataframe schema and system instructions into the prompt context. To stay within Groq's Free Tier Limits (100,000 Tokens Per Day), the tool docstrings and system instructions were heavily optimized (Token Diet) to reduce the payload footprint.
* **Streamlit State File Management:** Saving static images (e.g., `chart.png`) caused `MediaFileStorageError` during Streamlit reruns. This was solved by implementing a dynamic renaming mechanism using `time.time()` to ensure unique file histories.

## Future Improvements

* Transition the API infrastructure from the Free Tier to a commercial developer plan. This will completely bypass the 100,000 Tokens Per Day (TPD) ceiling and expand Request Per Minute (RPM) capacity to handle concurrent enterprise traffic.
* Expand the agent's capability to connect directly to relational databases (e.g., PostgreSQL, MySQL) rather than relying solely on flat static CSV files.
* Integrate advanced memory handling (such as `ConversationBufferMemory` or a Redis-backed chat history) to allow contextual follow-up questions without dramatically inflating the token payload.

## Tech Stack

* **Frontend:** Streamlit
* **LLM Orchestration:** LangChain
* **Language Model:** Groq API (`llama-3.3-70b-versatile`)
* **Data Processing:** Pandas, Matplotlib, Seaborn
* **Web Search:** DuckDuckGo Search API

## How to Run Locally

**1. Clone the repository**

First, clone this repository to your local machine and navigate into the project directory:

```bash
git clone https://github.com/Shabrinani/ai-business-intelligent-agent.git
cd ai-business-intelligent-agent
```

**2. Set up a virtual environment**

It is highly recommended to use a virtual environment to isolate project dependencies.

**Windows**

```bash
python -m venv venv
.\venv\Scripts\activate
```

**macOS/Linux**

```bash
python3 -m venv venv
source venv/bin/activate
```

Once activated, your terminal should display `(venv)` at the beginning of the line.

**3. Install dependencies**

Install all the required libraries listed in the `requirements.txt` file:

```bash
pip install -r requirements.txt
```

**4. Configure environment secrets**

1. Create a folder named `.streamlit` in the root directory.
2. Inside the `.streamlit` folder, create a file named `secrets.toml`.
3. Open `secrets.toml` and add your Groq API key:

```toml
GROQ_API_KEY = "your_groq_api_key_here"
```

**5. Run the application**

Launch the Streamlit web server by running:

```bash
streamlit run app.py
```
