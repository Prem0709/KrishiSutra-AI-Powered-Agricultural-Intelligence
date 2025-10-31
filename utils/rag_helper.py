import os
import yaml
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Load config for API key
config_path = os.path.join(os.path.dirname(__file__), "..", "config.yaml")
with open(config_path, "r") as f:
    config = yaml.safe_load(f)

GEMINI_API_KEY = config.get("google_api_key")
EMBEDDING_MODEL = config.get("embedding_model", "models/embedding-001")

if GEMINI_API_KEY:
    embeddings = GoogleGenerativeAIEmbeddings(
        model=EMBEDDING_MODEL,
        google_api_key=GEMINI_API_KEY
    )
else:
    raise ValueError("Missing Google API key in config.yaml")
