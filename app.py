import streamlit as st
import pandas as pd
import os
import time
from langchain_groq import ChatGroq
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.tools import tool
from langchain.agents import create_agent

# PAGE CONFIGURATION
st.set_page_config(page_title="AI Business Intelligence Agent", page_icon="📊", layout="wide")

# SECURE API KEY LOADING
os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]

# SESSION STATE INITIALIZATION
if "messages" not in st.session_state:
    st.session_state.messages = []
if "datasets" not in st.session_state:
    st.session_state.datasets = {}
if "data_loaded" not in st.session_state:
    st.session_state.data_loaded = False

# SIDEBAR
with st.sidebar:
    st.markdown("""
        <style>
            .sticky-header {
                position: sticky;
                top: 0;
                background-color: var(--secondary-background-color);
                z-index: 999;
                padding: 15px 0px 10px 0px;
                margin-top: -20px;
                border-bottom: 1px solid rgba(255, 255, 255, 0.2);
            }
        </style>
        
        <div class="sticky-header">
            <h2 style="margin: 0; font-weight: 600;">AI Business Intelligence Agent</h2>
        </div>
    """, unsafe_allow_html=True)
    
    # DATA PROFILING
    if st.session_state.data_loaded:
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.header("Data Profiling")
        
        file_options = list(st.session_state.datasets.keys())
        active_file = st.selectbox("Active File for Analysis:", file_options, label_visibility="collapsed")
        
        df_active = st.session_state.datasets[active_file]
        
        col_rows, col_cols = st.columns(2)
        with col_rows:
            st.metric(label="Total Rows", value=f"{df_active.shape[0]:,}")
        with col_cols:
            st.metric(label="Total Columns", value=df_active.shape[1])
        
        with st.expander("Column Details & Missing Data", expanded=True):
            info_df = pd.DataFrame({
                "Type": df_active.dtypes.astype(str),
                "Nulls": df_active.isnull().sum()
            })
            st.dataframe(info_df, use_container_width=True)
            
    else:
        st.markdown("<br>", unsafe_allow_html=True)
        st.caption("No active data. Please upload a CSV file first.")

# MAIN SCREEN

# STATE 1: Before File Upload
if not st.session_state.data_loaded:
    st.markdown("<h2 style='text-align: center; margin-top: 15vh;'>Hello, how can I help you today?</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray;'>Ask the agent to analyze trends, generate visual charts, and search the web for real-time business context.</p>", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col_center, col3 = st.columns([1, 2, 1])
    
    with col_center:
        up_col, btn_col = st.columns([6, 1])
        
        with up_col:
            uploaded_files = st.file_uploader(
                "Drop your data here", 
                type=["csv"], 
                accept_multiple_files=True
            )
            
        with btn_col:
            if uploaded_files:
                st.markdown("<div style='margin-top: 55px;'></div>", unsafe_allow_html=True)
                
                if st.button(" ", icon=":material/send:", help="Start Analysis", use_container_width=True, type="primary"):
                    for file in uploaded_files:
                        try:
                            st.session_state.datasets[file.name] = pd.read_csv(file, encoding='utf-8')
                        except UnicodeDecodeError:
                            file.seek(0)
                            st.session_state.datasets[file.name] = pd.read_csv(file, encoding='windows-1252')
                    st.session_state.data_loaded = True
                    st.rerun()
                                        
# STATE 2: After File Upload
else:
    current_file = active_file if 'active_file' in locals() else list(st.session_state.datasets.keys())[0]
    df = st.session_state.datasets[current_file]
    
    # AGENT INITIALIZATION
    llm = ChatGroq(temperature=0, model_name="llama-3.3-70b-versatile")
    pandas_agent = create_pandas_dataframe_agent(
        llm, 
        df, 
        verbose=False, 
        allow_dangerous_code=True, 
        handle_parsing_errors=True
    )
    search_engine = DuckDuckGoSearchRun()
    
    @tool
    def Data_Analyzer_Tool(query: str) -> str:
        """Extract exact numbers/trends from CSV. Input MUST be natural language (e.g., 'Total sales?'). NO SQL! Return data only, no code explanations."""
        return pandas_agent.invoke({"input": query})["output"]
    
    @tool
    def Internet_Search_Tool(query: str) -> str:
        """Search web for news/trends NOT in CSV. Input MUST be a simple text query. NO XML/JSON tags."""
        try:
            return search_engine.run(query)
        except Exception as e:
            return "Search blocked. Inform user web search is unavailable."
    
    @tool
    def Visualization_Tool(query: str) -> str:
        """Draw charts ONLY. No math. Input: visual description. NO XML/JSON tags."""
        viz_prompt = f"Draw: {query}. Use seaborn/matplotlib. Rules: figsize=(12,6), sns.set_theme('whitegrid'), rotate x-ticks 45deg, tight_layout(). Save exactly as 'chart.png'. NO code output."
        return pandas_agent.invoke({"input": viz_prompt})["output"]

    tools = [Data_Analyzer_Tool, Internet_Search_Tool, Visualization_Tool]
    orchestrator_agent = create_agent(model=llm, tools=tools)
    
    # System instruction
    system_instruction = """You are a Business Intelligence AI.
    Rules:
    1. Give exact numbers and data evidence.
    2. Use tools logically: Data_Analyzer_Tool for numbers, Visualization_Tool for charts.
    3. If chart requested, confirm it's saved as 'chart.png'.
    4. Output as a concise numbered list."""

# CHAT AREA
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "image" in message:
                st.image(message["image"])

    # Greeting & Prompt Library
    if not st.session_state.messages:
        st.markdown("<h2 style='text-align: center; margin-top: 5vh;'>Hello, how can I help you today?</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: gray;'>Choose one of the recommended analysis below to start quickly:</p>", unsafe_allow_html=True)
        
        st.markdown("""
            <style>
                /* Force all buttons inside layout columns to have a minimum height */
                div[data-testid="column"] button {
                    min-height: 110px;
                    height: 100%;
                    white-space: pre-wrap; /* Allows text to wrap nicely */
                }
            </style>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Summarize Performance\n(Calculate total sales & profit)", icon=":material/analytics:", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": "What is the total sales and total profit in this dataset? Give me the exact numbers."})
                st.rerun()
        with col2:
            if st.button("Analyze Category Trends\n(Find trends for each product category)", icon=":material/trending_up:", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": "Analyze the trend for each product category. Is it increasing or decreasing over time? Provide figures."})
                st.rerun()
        with col3:
            if st.button("Global Tech Retail Context\n(Search 2026 global retail news)", icon=":material/travel_explore:", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": "Search the internet to tell me how the global tech retail sector is growing or shifting in 2026."})
                st.rerun()

    # INPUT PROMPT HANDLING
    if user_input := st.chat_input("Ask a multi-step question about the uploaded data..."):
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.rerun()

    # ASSISTANT RESPONSE TRIGGER
    if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
        prompt = st.session_state.messages[-1]["content"]
        
        with st.chat_message("assistant"):
            with st.spinner("The Orchestrator is analyzing the data..."):
                try:
                    if os.path.exists("chart.png"):
                        os.remove("chart.png")

                    response = orchestrator_agent.invoke({
                        "messages": [
                            {"role": "system", "content": system_instruction},
                            {"role": "user", "content": prompt}
                        ]
                    })
                    
                    answer = response["messages"][-1].content
                    st.markdown(answer)
                    
                    image_path = None
                    if os.path.exists("chart.png"):
                        # Make a unique filename using timestamp
                        unique_filename = f"chart_{int(time.time())}.png"
                        
                        os.rename("chart.png", unique_filename)
                        
                        st.image(unique_filename)
                        image_path = unique_filename
                    
                    message_data = {"role": "assistant", "content": answer}
                    if image_path:
                        message_data["image"] = image_path
                        
                    st.session_state.messages.append(message_data)
                    st.rerun()

                except Exception as e:
                    st.error(f"Error processing request: {e}")