from utils.api_fetcher import fetch_data_gov_api
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
import google.generativeai as genai
import yaml
import os


def build_kcc_agent(api_key, limit=50):
    # Replace with actual resource ID from data.gov.in (KCC)
    df = fetch_data_gov_api(api_key, resource_id="cef25fe2-9231-4128-8aec-2c948fedd43f", format="xml", limit=limit)
    text_data = df.to_string(index=False)

    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
    docs = splitter.create_documents([text_data])

    # Use local HuggingFace embeddings (no API quota limits)
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    
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
    class KCCQAAgent:
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
            prompt = f"""You are an AI assistant for Kisan Call Centre (KCC).
            
            Context:
            {context}
            
            Question: {query}
            
            Provide a concise answer based on the context."""
            response = self.model.generate_content(prompt)
            return response.text if response else "No response generated."

    return KCCQAAgent(vectorstore, retriever, CHAT_MODEL)
