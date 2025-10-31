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

def build_agriculture_agent(file_path="data/Current Daily Price of Various Commodities from Various Markets (Mandi).csv"):
    df = load_data(file_path)

    # Create combined text
    text_data = " ".join(df.astype(str).apply(lambda x: ' | '.join(x), axis=1).tolist())

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    docs = splitter.create_documents([text_data])

    # Use local HuggingFace embeddings (no API quota limits)
    try:
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
    except Exception:
        # Fallback to OpenAI if needed
        embeddings = OpenAIEmbeddings()
    
    # Create the FAISS vectorstore
    vectorstore = FAISS.from_documents(docs, embeddings)
    
    # Create a retriever (but we'll use vectorstore directly for searches)
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
    class AgricultureQAAgent:
        def __init__(self, vectorstore, retriever, chat_model):
            self.vectorstore = vectorstore  # We'll use this for searching
            self.retriever = retriever
            self.model = genai.GenerativeModel(chat_model)

        def retrieve_context(self, query: str, k: int = 5) -> str:
            try:
                # Check if vectorstore has similarity_search method
                if hasattr(self.vectorstore, 'similarity_search'):
                    docs = self.vectorstore.similarity_search(query, k=k)
                # Otherwise use the retriever's invoke method
                elif hasattr(self.retriever, 'invoke'):
                    docs = self.retriever.invoke(query)
                # Or use the retriever's get_relevant_documents method
                elif hasattr(self.retriever, 'get_relevant_documents'):
                    docs = self.retriever.get_relevant_documents(query)
                else:
                    return "Could not retrieve documents: No valid retrieval method found."
                
                context = "\n\n".join([d.page_content for d in docs])
                return context
            except Exception as e:
                return f"Error during document retrieval: {str(e)}"

        def run(self, query: str) -> str:
            context = self.retrieve_context(query)
            prompt = f"""You are an AI assistant for agriculture.
            
            Context:
            {context}
            
            Question: {query}
            
            Provide a concise answer based on the context."""
            response = self.model.generate_content(prompt)
            return response.text if response else "No response generated."

    # Create and return the agent with both vectorstore and retriever
    return AgricultureQAAgent(vectorstore, retriever, CHAT_MODEL)
