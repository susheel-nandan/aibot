import os
import streamlit as st
from langchain_groq import ChatGroq
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver

from app.tools import rag_tool, booking_persistence_tool, email_tool

def get_agent_executor():
    # Setup LLM
    groq_api_key = st.secrets.get("GROQ_API_KEY", os.getenv("GROQ_API_KEY"))
    if not groq_api_key:
        raise ValueError("GROQ_API_KEY is missing. Please add it to .streamlit/secrets.toml")

    llm = ChatGroq(
        model="openai/gpt-oss-120b", 
        api_key=groq_api_key,
        temperature=0.2
    )

    # Define Tools
    tools = [rag_tool, booking_persistence_tool, email_tool]

    # System prompt
    system_prompt = """
    You are a friendly, helpful AI Booking Assistant for a Tech Consultation Clinic.
    Your job is to answer user questions using the `rag_tool` and help users book appointments.
    
    BOOKING FLOW:
    1. If the user wants to book an appointment, you must collect the following information:
       - Customer Name
       - Email
       - Phone
       - Booking/Service Type
       - Preferred Date (YYYY-MM-DD)
       - Preferred Time (HH:MM)
    2. Do NOT ask for all information at once. Have a natural multi-turn conversation. Ask for missing details one by one.
    3. Once you have ALL the required details, summarize them for the user and ask for explicit confirmation (e.g., "Should I go ahead and book this?").
    4. Only AFTER the user confirms, use the `booking_persistence_tool` to save the booking to the database.
    5. After the booking is saved successfully, use the `email_tool` to send a confirmation email to the user.
       - Use a nice subject line and include all booking details in the email body.
    6. Finally, give the user their Booking ID and tell them the email was sent (or if it failed, inform them the booking is saved but email delivery failed).

    If the user asks general questions about the clinic (services, prices, FAQs), use the `rag_tool`.
    """
    
    # Memory
    if "memory_saver" not in st.session_state:
        st.session_state.memory_saver = MemorySaver()

    agent = create_react_agent(llm, tools, prompt=system_prompt, checkpointer=st.session_state.memory_saver)
    
    return agent

def process_message(user_input: str) -> str:
    agent = get_agent_executor()
    try:
        config = {"configurable": {"thread_id": "streamlit_session"}}
        response = agent.invoke({"messages": [("user", user_input)]}, config=config)
        return response["messages"][-1].content
    except Exception as e:
        return f"An error occurred: {str(e)}"
