import os
import yaml
import pandas as pd
import google.generativeai as genai

from langchain_community.document_loaders import CSVLoader
from langchain_google_genai.embeddings import GoogleGenerativeAIEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter


# ============================================================
# 1️⃣ Load Config from config.yaml
# ============================================================
def load_config():
    config_path = os.path.join(os.path.dirname(__file__), "..", "config.yaml")
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


config = load_config()
GEMINI_API_KEY = config.get("google_api_key")
EMBEDDING_MODEL = config.get("embedding_model", "models/embedding-001")

CHAT_MODEL = config.get("chat_model", "models/gemini-pro-latest")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    raise ValueError("❌ Missing Google API key in config.yaml")


# ============================================================
# 2️⃣ Helper — Load CSV or other file formats
# ============================================================
def load_dataset(file_path: str):
    """Loads a dataset from CSV, Excel, JSON, or Parquet."""
    ext = os.path.splitext(file_path)[-1].lower()

    if ext == ".csv":
        return pd.read_csv(file_path)
    elif ext in [".xlsx", ".xls"]:
        return pd.read_excel(file_path)
    elif ext == ".json":
        return pd.read_json(file_path)
    elif ext == ".parquet":
        return pd.read_parquet(file_path)
    else:
        raise ValueError(f"Unsupported file type: {ext}")


# ============================================================
# 3️⃣ Climate Agent Builder
# ============================================================
class ClimateRAGAgent:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.vectorstore = None
        self._build_vector_index()

    def _build_vector_index(self):
        """Creates or loads a FAISS vector index for retrieval."""
        file_name = os.path.splitext(os.path.basename(self.file_path))[0]
        index_path = os.path.join(os.path.dirname(self.file_path), f"{file_name}.faiss")

        # Use local HuggingFace embeddings (no API quota limits)
        try:
            embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2"
            )
        except Exception:
            # Fallback to Google embeddings if needed
            embeddings = GoogleGenerativeAIEmbeddings(
                model=EMBEDDING_MODEL, google_api_key=GEMINI_API_KEY
            )

        if os.path.exists(index_path):
            # Load existing vector store
            self.vectorstore = FAISS.load_local(
                index_path, embeddings, allow_dangerous_deserialization=True
            )

        else:
            # Build and save vector store
            df = load_dataset(self.file_path)
            text_data = "\n".join(
                df.astype(str).apply(lambda x: ", ".join(x), axis=1).tolist()
            )

            splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
            chunks = splitter.split_text(text_data)

            self.vectorstore = FAISS.from_texts(chunks, embedding=embeddings)
            self.vectorstore.save_local(index_path)

    def retrieve_context(self, query: str) -> str:
        """Retrieve top relevant context for a given query."""
        try:
            docs = self.vectorstore.similarity_search(query, k=4)
            context = "\n\n".join([d.page_content for d in docs])
            return context
        except Exception as e:
            st.error(f"Error during document retrieval: {str(e)}")
            return ""
    
    def run(self, query: str) -> str:
        """Generate answer using retrieved context and Gemini."""
        context = self.retrieve_context(query)
        prompt = f"""You are an AI assistant for climate and weather data.
        
        Context:
        {context}
        
        Question: {query}
        
        Provide a concise answer based on the context."""
        model = genai.GenerativeModel(CHAT_MODEL)
        response = model.generate_content(prompt)
        return response.text if response else "No response generated."


# ============================================================
# 4️⃣ Builder Function (used in main_app.py)
# ============================================================
def build_climate_agent(file_path: str = "data/Mean_Temp_IMD_2017.csv"):
    """
    Build and return a climate data RAG agent.
    This reads CSV/Excel/JSON data and creates a vector index for QA.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"❌ Data file not found: {file_path}")

    agent = ClimateRAGAgent(file_path)
    return agent
