from utils.data_loader import load_data
# from langchain.embeddings import OpenAIEmbeddings
from langchain_openai import OpenAIEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings
import google.generativeai as genai
import yaml
import os

# from langchain.vectorstores import FAISS
from langchain_community.vectorstores import FAISS

# from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_text_splitters import RecursiveCharacterTextSplitter

# from langchain.chains import RetrievalQA
from langchain_classic.chains import RetrievalQA

# from langchain.chat_models import ChatOpenAI
from langchain_openai import ChatOpenAI


def build_scheme_agent(file_path="data/GetPMKisanDatagov.json"):
    df = load_data(file_path)
    text_data = df.to_string(index=False)

    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=80)
    docs = splitter.create_documents([text_data])

    # Use local HuggingFace embeddings (no API quota limits)
    try:
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
    except Exception:
        # Fallback to OpenAI if needed
        embeddings = OpenAIEmbeddings()
    
    vectorstore = FAISS.from_documents(docs, embeddings)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

    # Load config for Gemini
    config_path = os.path.join(os.path.dirname(__file__), "..", "config.yaml")
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    
    # Use Gemini instead of OpenAI
    GEMINI_API_KEY = config.get("google_api_key")
    CHAT_MODEL = config.get("chat_model", "models/gemini-pro-latest")
    if GEMINI_API_KEY:
        genai.configure(api_key=GEMINI_API_KEY)
    
    # Create custom QA wrapper for Gemini
    class SchemeQAAgent:
        def __init__(self, vectorstore, retriever, chat_model):
            self.vectorstore = vectorstore
            self.retriever = retriever
            self.model = genai.GenerativeModel(chat_model)

        def retrieve_context(self, query: str, k: int = 5) -> str:
            docs = self.vectorstore.similarity_search(query, k=k)
            context = "\n\n".join([d.page_content for d in docs])
            return context

        def run(self, query: str) -> str:
            context = self.retrieve_context(query)
            prompt = f"""You are an AI assistant for government schemes.
            
            Context:
            {context}
            
            Question: {query}
            
            Provide a concise answer based on the context."""
            response = self.model.generate_content(prompt)
            return response.text if response else "No response generated."

    return SchemeQAAgent(vectorstore, retriever, CHAT_MODEL)
