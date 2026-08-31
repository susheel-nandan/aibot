import os
import tempfile
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
import streamlit as st

def process_uploaded_pdfs(uploaded_files):
    """
    Takes a list of Streamlit UploadedFiles, saves them temporarily,
    extracts text, chunks it, and stores in Chroma DB.
    """
    if not uploaded_files:
        return None

    documents = []
    
    # Save uploaded files to a temporary directory to use PyPDFLoader
    with tempfile.TemporaryDirectory() as temp_dir:
        for uploaded_file in uploaded_files:
            temp_path = os.path.join(temp_dir, uploaded_file.name)
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            loader = PyPDFLoader(temp_path)
            docs = loader.load()
            documents.extend(docs)
    
    if not documents:
        return None

    # Chunk the text
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    splits = text_splitter.split_documents(documents)
    
    # Create embeddings and store in Chroma
    # Make sure GEMINI_API_KEY is available in env or secrets
    gemini_api_key = st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY"))
    if not gemini_api_key:
        raise ValueError("GEMINI_API_KEY is missing.")

    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-2", 
        google_api_key=gemini_api_key
    )
    
    # Create or update vector store (persist directory is ./chroma_db)
    vectorstore = Chroma.from_documents(
        documents=splits,
        embedding=embeddings,
        persist_directory="./chroma_db"
    )
    
    return vectorstore

def get_retriever():
    """Returns a retriever from the existing vector store."""
    gemini_api_key = st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY"))
    if not gemini_api_key:
        return None
        
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-2", 
        google_api_key=gemini_api_key
    )
    
    if os.path.exists("./chroma_db"):
        vectorstore = Chroma(
            persist_directory="./chroma_db", 
            embedding_function=embeddings
        )
        return vectorstore.as_retriever(search_kwargs={"k": 3})
    return None
