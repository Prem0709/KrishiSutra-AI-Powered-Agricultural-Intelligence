import streamlit as st
import yaml
import google.generativeai as genai
import os

from agents.climate_agent import build_climate_agent
from agents.agriculture_agent import build_agriculture_agent
from agents.scheme_agent import build_scheme_agent
from agents.kcc_agent import build_kcc_agent
from utils.api_fetcher import fetch_data_gov_api


# ----------------------------------
# 1️⃣ Load Configurations
# ----------------------------------
def load_config():
    config_path = os.path.join(os.path.dirname(__file__), "config.yaml")
    with open(config_path, "r") as f:
        return yaml.safe_load(f)

config = load_config()

# Read keys and parameters
DATA_GOV_API_KEY = config["data_gov"]["api_key"]
LLM_PROVIDER = config.get("llm_provider", "gemini")
GEMINI_API_KEY = config.get("google_api_key")
EMBEDDING_MODEL = config.get("embedding_model", "models/embedding-001")
EMBEDDING_PROVIDER = config.get("embedding_provider", "huggingface")
CHAT_MODEL = config.get("chat_model", "models/gemini-pro-latest")

# ✅ Configure Gemini API
if LLM_PROVIDER.lower() == "gemini" and GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    st.sidebar.success(f"✅ Gemini Configured ({CHAT_MODEL})")
    st.sidebar.info(f"📊 Embeddings: {EMBEDDING_PROVIDER.upper()}")
else:
    st.sidebar.error("❌ Gemini API key missing or provider not set to 'gemini'.")


# ----------------------------------
# 2️⃣ Streamlit UI Setup
# ----------------------------------
st.set_page_config(page_title="🌾 Project Samarth", layout="wide")

# Center align the title and subtitle
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown("<h1 style='text-align: center;'>🌾 Project Samarth</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>KrishiSutra AI-Powered Agricultural Intelligence</h3>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'><i>Powered by Gemini + Multi-Agent RAG</i></p>", unsafe_allow_html=True)

# Add a divider
st.divider()

st.sidebar.header("⚙️ Configuration")
agent_choice = st.sidebar.selectbox(
    "Select Knowledge Agent:",
    ["Auto Detect", "🌦️ Climate Agent", "🌾 Agriculture Agent", "🧾 Scheme Agent", "☎️ KCC Agent"]
)

uploaded_file = st.sidebar.file_uploader(
    "📤 Upload Custom Dataset (CSV, Excel, JSON, ZIP)",
    type=["csv", "xlsx", "xls", "json", "zip"],
)

if GEMINI_API_KEY:
    st.sidebar.success("✅ Gemini API key loaded")
else:
    st.sidebar.error("❌ Missing Gemini API key")


# ----------------------------------
# 3️⃣ Agent Initializer
# ----------------------------------
@st.cache_resource(show_spinner=False)
def get_agent(agent_choice, api_key=None, uploaded_file=None):
    """Dynamically build and return the chosen RAG agent"""
    temp_path = None

    # Save uploaded file for use
    if uploaded_file:
        temp_path = f"data/{uploaded_file.name}"
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.read())
        st.sidebar.success(f"✅ Loaded file: {uploaded_file.name}")

    if agent_choice == "🌦️ Climate Agent":
        return build_climate_agent(temp_path or "data/Mean_Temp_IMD_2017.csv")

    elif agent_choice == "🌾 Agriculture Agent":
        return build_agriculture_agent(temp_path or "data/Current Daily Price of Various Commodities from Various Markets (Mandi).csv")

    elif agent_choice == "🧾 Scheme Agent":
        return build_scheme_agent(temp_path or "data/GetPMKisanDatagov.json")

    elif agent_choice == "☎️ KCC Agent":
        if api_key:
            return build_kcc_agent(api_key)
        else:
            st.error("❌ Missing data.gov.in API key for KCC Agent.")
            return None

    return None


# ----------------------------------
# 4️⃣ Auto Agent Detection
# ----------------------------------
def auto_select_agent(user_query):
    query = user_query.lower()
    if any(word in query for word in ["rain", "temperature", "climate", "weather"]):
        return "🌦️ Climate Agent"
    elif any(word in query for word in ["crop", "yield", "price", "production", "agriculture"]):
        return "🌾 Agriculture Agent"
    elif any(word in query for word in ["scheme", "pmkisan", "subsidy", "beneficiary"]):
        return "🧾 Scheme Agent"
    elif any(word in query for word in ["kcc", "helpline", "call centre"]):
        return "☎️ KCC Agent"
    else:
        return None


# ----------------------------------
# 5️⃣ Gemini Response Helper
# ----------------------------------
def gemini_answer(prompt, context=""):
    """Uses Gemini 1.5 model to generate a clean, factual answer"""
    try:
        # Use the configured model from config.yaml (CHAT_MODEL). Example: 'models/gemini-pro-latest'
        model = genai.GenerativeModel(CHAT_MODEL)
        full_prompt = f"""
        You are an AI assistant for smart agriculture.
        Use the following context to answer the question accurately.

        Context:
        {context}

        Question:
        {prompt}

        Provide a concise, factual, and human-readable answer.
        """
        response = model.generate_content(full_prompt)
        return response.text or "⚠️ No response generated."
    except Exception as e:
        return f"❌ Error: {str(e)}"


# ----------------------------------
# 6️⃣ Chat Interface
# ----------------------------------

# Initialize chat history in session state if it doesn't exist
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

st.markdown("## 💬 Chat with Samarth AI")

# Chat history display
for i, (query, response) in enumerate(st.session_state.chat_history):
    with st.container():
        # User message
        st.markdown(f"**You:** {query}")
        # Assistant response
        st.markdown(f"**Samarth:** {response}")
        st.divider()

# Chat input area with clear button
col1, col2 = st.columns([5,1])
with col1:
    user_query = st.text_input("Ask your question (e.g., 'Compare rainfall and rice yield in Maharashtra')")
with col2:
    if st.button("Clear Chat"):
        st.session_state.chat_history = []
        st.rerun()

if st.button("Submit", type="primary") and user_query:
    with st.spinner("🔎 Analyzing and fetching data..."):
        # Step 1: Auto-select agent
        selected_agent = agent_choice
        if agent_choice == "Auto Detect":
            selected_agent = auto_select_agent(user_query)

        if not selected_agent:
            st.warning("🤖 Could not auto-detect domain. Please select an agent manually.")
            st.stop()

        # Step 2: Initialize selected agent
        qa_agent = get_agent(selected_agent, DATA_GOV_API_KEY, uploaded_file)

        if not qa_agent:
            st.error("❌ Failed to initialize selected agent.")
            st.stop()

        # Step 3: Retrieve domain-specific context
        try:
            context = qa_agent.retrieve_context(user_query)
        except AttributeError:
            # Fallback: if old `.run()` method exists
            context = qa_agent.run(user_query)

        # Step 4: Use Gemini to generate final answer
        final_answer = gemini_answer(user_query, context)
        
        # Add the Q&A pair to chat history
        st.session_state.chat_history.append((user_query, final_answer))
        
        # Show the latest response
        st.success("✅ Latest Response:")
        st.write(final_answer)


# ----------------------------------
# 7️⃣ Footer
# ----------------------------------
st.sidebar.markdown("---")
st.sidebar.caption("👨‍💻 Developed by Premkumar Pawar | Multi-Agent RAG with Gemini")







































# import streamlit as st
# import yaml
# import google.generativeai as genai
# import os

# from agents.climate_agent import build_climate_agent
# from agents.agriculture_agent import build_agriculture_agent
# from agents.scheme_agent import build_scheme_agent
# from agents.kcc_agent import build_kcc_agent
# from utils.api_fetcher import fetch_data_gov_api


# # ----------------------------------
# # 1️⃣ Load Configurations
# # ----------------------------------
# def load_config():
#     config_path = os.path.join(os.path.dirname(__file__), "config.yaml")
#     with open(config_path, "r") as f:
#         return yaml.safe_load(f)

# config = load_config()

# # Read keys and parameters
# DATA_GOV_API_KEY = config["data_gov"]["api_key"]
# LLM_PROVIDER = config.get("llm_provider", "gemini")
# GEMINI_API_KEY = config.get("google_api_key")
# EMBEDDING_MODEL = config.get("embedding_model", "models/embedding-001")
# EMBEDDING_PROVIDER = config.get("embedding_provider", "huggingface")
# CHAT_MODEL = config.get("chat_model", "models/gemini-pro-latest")

# # ✅ Configure Gemini API
# if LLM_PROVIDER.lower() == "gemini" and GEMINI_API_KEY:
#     genai.configure(api_key=GEMINI_API_KEY)
#     st.sidebar.success(f"✅ Gemini Configured ({CHAT_MODEL})")
#     st.sidebar.info(f"📊 Embeddings: {EMBEDDING_PROVIDER.upper()}")
# else:
#     st.sidebar.error("❌ Gemini API key missing or provider not set to 'gemini'.")


# # ----------------------------------
# # 2️⃣ Streamlit UI Setup
# # ----------------------------------
# st.set_page_config(page_title="🌾 Project Samarth — Gemini Multi-RAG", layout="wide")
# st.title("🌾 Project Samarth — AI Q&A Assistant (Gemini Powered)")
# st.caption("Empowering Smart Agriculture using Multi-Agent RAG and Google Gemini")

# st.sidebar.header("⚙️ Configuration")
# agent_choice = st.sidebar.selectbox(
#     "Select Knowledge Agent:",
#     ["Auto Detect", "🌦️ Climate Agent", "🌾 Agriculture Agent", "🧾 Scheme Agent", "☎️ KCC Agent"]
# )

# uploaded_file = st.sidebar.file_uploader(
#     "📤 Upload Custom Dataset (CSV, Excel, JSON, ZIP)",
#     type=["csv", "xlsx", "xls", "json", "zip"],
# )

# if GEMINI_API_KEY:
#     st.sidebar.success("✅ Gemini API key loaded")
# else:
#     st.sidebar.error("❌ Missing Gemini API key")


# # ----------------------------------
# # 3️⃣ Agent Initializer
# # ----------------------------------
# @st.cache_resource(show_spinner=False)
# def get_agent(agent_choice, api_key=None, uploaded_file=None):
#     """Dynamically build and return the chosen RAG agent"""
#     temp_path = None

#     # Save uploaded file for use
#     if uploaded_file:
#         temp_path = f"data/{uploaded_file.name}"
#         with open(temp_path, "wb") as f:
#             f.write(uploaded_file.read())
#         st.sidebar.success(f"✅ Loaded file: {uploaded_file.name}")

#     if agent_choice == "🌦️ Climate Agent":
#         return build_climate_agent(temp_path or "data/Mean_Temp_IMD_2017.csv")

#     elif agent_choice == "🌾 Agriculture Agent":
#         return build_agriculture_agent(temp_path or "data/Current Daily Price of Various Commodities from Various Markets (Mandi).csv")

#     elif agent_choice == "🧾 Scheme Agent":
#         return build_scheme_agent(temp_path or "data/GetPMKisanDatagov.json")

#     elif agent_choice == "☎️ KCC Agent":
#         if api_key:
#             return build_kcc_agent(api_key)
#         else:
#             st.error("❌ Missing data.gov.in API key for KCC Agent.")
#             return None

#     return None


# # ----------------------------------
# # 4️⃣ Auto Agent Detection
# # ----------------------------------
# def auto_select_agent(user_query):
#     query = user_query.lower()
#     if any(word in query for word in ["rain", "temperature", "climate", "weather"]):
#         return "🌦️ Climate Agent"
#     elif any(word in query for word in ["crop", "yield", "price", "production", "agriculture"]):
#         return "🌾 Agriculture Agent"
#     elif any(word in query for word in ["scheme", "pmkisan", "subsidy", "beneficiary"]):
#         return "🧾 Scheme Agent"
#     elif any(word in query for word in ["kcc", "helpline", "call centre"]):
#         return "☎️ KCC Agent"
#     else:
#         return None


# # ----------------------------------
# # 5️⃣ Gemini Response Helper
# # ----------------------------------
# def gemini_answer(prompt, context=""):
#     """Uses Gemini 1.5 model to generate a clean, factual answer"""
#     try:
#         # Use the configured model from config.yaml (CHAT_MODEL). Example: 'models/gemini-pro-latest'
#         model = genai.GenerativeModel(CHAT_MODEL)
#         full_prompt = f"""
#         You are an AI assistant for smart agriculture.
#         Use the following context to answer the question accurately.

#         Context:
#         {context}

#         Question:
#         {prompt}

#         Provide a concise, factual, and human-readable answer.
#         """
#         response = model.generate_content(full_prompt)
#         return response.text or "⚠️ No response generated."
#     except Exception as e:
#         return f"❌ Error: {str(e)}"


# # ----------------------------------
# # 6️⃣ Chat Interface
# # ----------------------------------
# st.markdown("## 💬 Chat with Samarth AI")
# user_query = st.text_input("Ask your question (e.g., 'Compare rainfall and rice yield in Maharashtra')")

# if st.button("Submit") and user_query:
#     with st.spinner("🔎 Analyzing and fetching data..."):
#         # Step 1: Auto-select agent
#         selected_agent = agent_choice
#         if agent_choice == "Auto Detect":
#             selected_agent = auto_select_agent(user_query)

#         if not selected_agent:
#             st.warning("🤖 Could not auto-detect domain. Please select an agent manually.")
#             st.stop()

#         # Step 2: Initialize selected agent
#         qa_agent = get_agent(selected_agent, DATA_GOV_API_KEY, uploaded_file)

#         if not qa_agent:
#             st.error("❌ Failed to initialize selected agent.")
#             st.stop()

#         # Step 3: Retrieve domain-specific context
#         try:
#             context = qa_agent.retrieve_context(user_query)
#         except AttributeError:
#             # Fallback: if old `.run()` method exists
#             context = qa_agent.run(user_query)

#         # Step 4: Use Gemini to generate final answer
#         final_answer = gemini_answer(user_query, context)
#         st.success("✅ Response:")
#         st.write(final_answer)


# # ----------------------------------
# # 7️⃣ Footer
# # ----------------------------------
# st.sidebar.markdown("---")
# st.sidebar.caption("👨‍💻 Developed by Premkumar Pawar | Multi-Agent RAG with Gemini")
