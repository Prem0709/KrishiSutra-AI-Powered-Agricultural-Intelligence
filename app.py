import gradio as gr
import yaml
import google.generativeai as genai
import os

from agents.climate_agent import build_climate_agent
from agents.agriculture_agent import build_agriculture_agent
from agents.scheme_agent import build_scheme_agent
from agents.kcc_agent import build_kcc_agent


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
else:
    raise ValueError("❌ Gemini API key missing or provider not set to 'gemini'.")


# ----------------------------------
# 2️⃣ Agent Cache
# ----------------------------------
agent_cache = {}

def get_agent(agent_choice, uploaded_file=None):
    """Dynamically build and return the chosen RAG agent"""
    temp_path = None

    # Save uploaded file for use
    if uploaded_file:
        temp_path = f"data/{os.path.basename(uploaded_file.name)}"
        os.makedirs("data", exist_ok=True)
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.read())

    cache_key = f"{agent_choice}_{temp_path or 'default'}"
    
    if cache_key in agent_cache:
        return agent_cache[cache_key]

    if agent_choice == "🌦️ Climate Agent":
        agent = build_climate_agent(temp_path or "data/Mean_Temp_IMD_2017.csv")
    elif agent_choice == "🌾 Agriculture Agent":
        agent = build_agriculture_agent(temp_path or "data/Current Daily Price of Various Commodities from Various Markets (Mandi).csv")
    elif agent_choice == "🧾 Scheme Agent":
        agent = build_scheme_agent(temp_path or "data/GetPMKisanDatagov.json")
    elif agent_choice == "☎️ KCC Agent":
        agent = build_kcc_agent(DATA_GOV_API_KEY) if DATA_GOV_API_KEY else None
    else:
        agent = None

    if agent:
        agent_cache[cache_key] = agent
    
    return agent


# ----------------------------------
# 3️⃣ Auto Agent Detection
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
        return "🌾 Agriculture Agent"  # Default fallback


# ----------------------------------
# 4️⃣ Gemini Response Helper
# ----------------------------------
def gemini_answer(prompt, context=""):
    """Uses Gemini 1.5 model to generate a clean, factual answer"""
    try:
        model = genai.GenerativeModel(CHAT_MODEL)
        full_prompt = f"""
You are an AI assistant for smart agriculture - KrishiSutra.
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
# 5️⃣ Chat Handler
# ----------------------------------
def chat_handler(user_query, agent_choice, uploaded_file, chat_history):
    """Process user query and return response"""
    
    if not user_query or user_query.strip() == "":
        return chat_history, ""
    
    # Step 1: Auto-select agent if needed
    selected_agent = agent_choice
    if agent_choice == "Auto Detect":
        selected_agent = auto_select_agent(user_query)

    # Step 2: Initialize selected agent
    qa_agent = get_agent(selected_agent, uploaded_file)

    if not qa_agent:
        error_msg = f"❌ Failed to initialize {selected_agent}"
        chat_history.append((user_query, error_msg))
        return chat_history, ""

    # Step 3: Retrieve domain-specific context
    try:
        if hasattr(qa_agent, 'retrieve_context'):
            context = qa_agent.retrieve_context(user_query)
        else:
            context = qa_agent.run(user_query)
    except Exception as e:
        error_msg = f"❌ Error retrieving context: {str(e)}"
        chat_history.append((user_query, error_msg))
        return chat_history, ""

    # Step 4: Use Gemini to generate final answer
    final_answer = gemini_answer(user_query, context)
    
    # Add to chat history
    chat_history.append((user_query, final_answer))
    
    return chat_history, ""


# ----------------------------------
# 6️⃣ Gradio Interface
# ----------------------------------
def build_gradio_app():
    """Build the Gradio UI"""
    
    with gr.Blocks(theme=gr.themes.Soft(), title="🌾 KrishiSutra AI") as demo:
        gr.Markdown(
            """
            # 🌾 Project Samarth - KrishiSutra AI
            ### AI-Powered Agricultural Intelligence
            *Powered by Gemini + Multi-Agent RAG*
            
            Ask questions about climate, agriculture, government schemes, and more!
            """
        )
        
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### ⚙️ Configuration")
                
                agent_choice = gr.Dropdown(
                    choices=["Auto Detect", "🌦️ Climate Agent", "🌾 Agriculture Agent", "🧾 Scheme Agent", "☎️ KCC Agent"],
                    value="Auto Detect",
                    label="Select Knowledge Agent",
                    interactive=True
                )
                
                uploaded_file = gr.File(
                    label="📤 Upload Custom Dataset",
                    file_types=[".csv", ".xlsx", ".xls", ".json"],
                    type="filepath"
                )
                
                gr.Markdown(
                    f"""
                    **Status:**
                    - ✅ Gemini Configured ({CHAT_MODEL})
                    - 📊 Embeddings: {EMBEDDING_PROVIDER.upper()}
                    """
                )
                
                gr.Markdown(
                    """
                    ### 💡 Example Questions:
                    - Compare rainfall in Tamil Nadu and Kerala
                    - What is the rice yield in Maharashtra?
                    - List government schemes for farmers
                    - Show crop prices in Karnataka
                    """
                )
            
            with gr.Column(scale=2):
                gr.Markdown("### 💬 Chat with Samarth AI")
                
                chatbot = gr.Chatbot(
                    label="Conversation",
                    height=500,
                    show_copy_button=True
                )
                
                with gr.Row():
                    user_input = gr.Textbox(
                        placeholder="Ask your question (e.g., 'Compare rainfall and rice yield in Maharashtra')",
                        label="Your Question",
                        lines=2,
                        scale=4
                    )
                
                with gr.Row():
                    submit_btn = gr.Button("Submit", variant="primary", scale=1)
                    clear_btn = gr.Button("Clear Chat", scale=1)
        
        # Event handlers
        submit_btn.click(
            fn=chat_handler,
            inputs=[user_input, agent_choice, uploaded_file, chatbot],
            outputs=[chatbot, user_input]
        )
        
        user_input.submit(
            fn=chat_handler,
            inputs=[user_input, agent_choice, uploaded_file, chatbot],
            outputs=[chatbot, user_input]
        )
        
        clear_btn.click(
            fn=lambda: ([], ""),
            inputs=None,
            outputs=[chatbot, user_input]
        )
        
        gr.Markdown(
            """
            ---
            👨‍💻 Developed by Premkumar Pawar | Multi-Agent RAG with Gemini
            """
        )
    
    return demo


# ----------------------------------
# 7️⃣ Launch
# ----------------------------------
if __name__ == "__main__":
    demo = build_gradio_app()
    demo.launch()
