import streamlit as st
import os
import sys

# Add project root to sys.path to resolve ModuleNotFoundError on Streamlit Cloud
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Set page config at the very beginning
st.set_page_config(page_title="AI Booking Assistant", page_icon="📅", layout="wide")

from app.chat_logic import process_message
from app.rag_pipeline import process_uploaded_pdfs
from app.admin_dashboard import admin_dashboard
from db.database import init_db

# Initialize database
init_db()

def main():
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Chatbot", "Admin Dashboard"])

    if page == "Admin Dashboard":
        admin_dashboard()
    else:
        st.title("🤖 Tech Clinic AI Assistant")
        st.write("I can answer your questions about our services and help you book an appointment!")

        # Sidebar for PDF Upload
        st.sidebar.header("Knowledge Base Setup (RAG)")
        uploaded_files = st.sidebar.file_uploader(
            "Upload FAQs/Policy PDFs", 
            type=["pdf"], 
            accept_multiple_files=True
        )
        
        if st.sidebar.button("Process PDFs"):
            if uploaded_files:
                with st.spinner("Processing PDFs and building Knowledge Base..."):
                    try:
                        process_uploaded_pdfs(uploaded_files)
                        st.sidebar.success("PDFs processed successfully!")
                    except Exception as e:
                        st.sidebar.error(f"Error processing PDFs: {str(e)}")
            else:
                st.sidebar.warning("Please upload at least one PDF first.")

        # Chat Interface
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # Display chat messages from history on app rerun
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # React to user input
        if prompt := st.chat_input("Hi! How can I help you today?"):
            # Display user message in chat message container
            st.chat_message("user").markdown(prompt)
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})

            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response = process_message(prompt)
                st.markdown(response)
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main()
