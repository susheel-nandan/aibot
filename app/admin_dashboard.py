import streamlit as st
import pandas as pd
from db.database import SessionLocal
from db.models import Booking, Customer

def admin_dashboard():
    st.title("Admin Dashboard - Bookings")
    st.write("View and manage all clinic bookings.")

    db = SessionLocal()
    try:
        # Fetch data
        bookings = db.query(
            Booking.id, 
            Customer.name, 
            Customer.email, 
            Booking.booking_type, 
            Booking.date, 
            Booking.time, 
            Booking.status
        ).join(Customer).all()
        
        if not bookings:
            st.info("No bookings found in the database.")
            return

        # Convert to DataFrame
        df = pd.DataFrame(bookings, columns=["Booking ID", "Name", "Email", "Service", "Date", "Time", "Status"])
        
        # Filters
        st.subheader("Filter Bookings")
        col1, col2, col3 = st.columns(3)
        with col1:
            name_filter = st.text_input("Filter by Name")
        with col2:
            email_filter = st.text_input("Filter by Email")
        with col3:
            date_filter = st.date_input("Filter by Date", value=None)

        # Apply filters
        if name_filter:
            df = df[df["Name"].str.contains(name_filter, case=False, na=False)]
        if email_filter:
            df = df[df["Email"].str.contains(email_filter, case=False, na=False)]
        if date_filter:
            df = df[df["Date"] == str(date_filter)]

        st.dataframe(df, use_container_width=True)

    except Exception as e:
        st.error(f"Failed to load bookings: {str(e)}")
    finally:
        db.close()
