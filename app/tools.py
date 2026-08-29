import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from langchain.tools import tool
import streamlit as st
from db.database import SessionLocal
from db.models import Customer, Booking
from app.rag_pipeline import get_retriever

@tool
def rag_tool(query: str) -> str:
    """Useful for answering questions about the clinic's services, policies, or general FAQs based on the uploaded PDFs."""
    retriever = get_retriever()
    if not retriever:
        return "I'm sorry, but I don't have any documents loaded right now to answer that question."
    
    docs = retriever.invoke(query)
    if not docs:
        return "I couldn't find any relevant information in my knowledge base."
    
    return "\n\n".join([doc.page_content for doc in docs])

@tool
def booking_persistence_tool(name: str, email: str, phone: str, booking_type: str, date: str, time: str) -> str:
    """Saves the structured booking payload to the database. Call this ONLY after the user has explicitly confirmed all booking details."""
    db = SessionLocal()
    try:
        # Check if customer exists
        customer = db.query(Customer).filter(Customer.email == email).first()
        if not customer:
            customer = Customer(name=name, email=email, phone=phone)
            db.add(customer)
            db.commit()
            db.refresh(customer)
        
        # Create booking
        booking = Booking(
            customer_id=customer.customer_id,
            booking_type=booking_type,
            date=date,
            time=time,
            status="Confirmed"
        )
        db.add(booking)
        db.commit()
        db.refresh(booking)
        
        return f"SUCCESS: Booking confirmed. Booking ID is {booking.id}."
    except Exception as e:
        db.rollback()
        return f"ERROR: Failed to save booking to database. Details: {str(e)}"
    finally:
        db.close()

@tool
def email_tool(to_email: str, subject: str, body: str) -> str:
    """Sends a confirmation email to the user."""
    # Assuming Streamlit secrets are set
    try:
        smtp_email = st.secrets["smtp"]["email"]
        smtp_password = st.secrets["smtp"]["password"]
        
        if smtp_password == "YOUR_APP_PASSWORD_HERE":
            return "ERROR: Email could not be sent because the SMTP app password is not configured."

        msg = MIMEMultipart()
        msg['From'] = smtp_email
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(smtp_email, smtp_password)
        text = msg.as_string()
        server.sendmail(smtp_email, to_email, text)
        server.quit()
        
        return "SUCCESS: Email sent."
    except Exception as e:
        return f"ERROR: Email delivery failed. Details: {str(e)}"
