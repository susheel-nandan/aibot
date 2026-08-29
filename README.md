# AI Booking Assistant

This is an AI-driven Booking Assistant built using Streamlit, LangChain, and Google Gemini.

## Features
- **RAG Chatbot**: Upload a PDF via the sidebar to feed the AI knowledge about your business (e.g., FAQs, pricing, services).
- **Conversational Booking**: The AI naturally asks for missing booking details (Name, Email, Phone, Service, Date, Time).
- **Short-Term Memory**: The AI remembers the context of the conversation.
- **SQLite Database**: Bookings are persistently saved.
- **Email Confirmation**: Sends an automatic email summary upon booking via SMTP.
- **Admin Dashboard**: Switch to the Admin Dashboard from the sidebar to view, search, and filter all bookings.

## Setup Instructions

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Secrets**
   Open `.streamlit/secrets.toml` and configure your credentials:
   - `GEMINI_API_KEY`: Your Google Gemini API key.
   - `[smtp] email`: Your Gmail address (e.g., `susheelnandan@gmail.com`).
   - `[smtp] password`: Your Gmail **App Password** (Requires 2FA to be enabled on your Google account. Do NOT use your regular login password).

3. **Run the Application**
   ```bash
   streamlit run app/main.py
   ```

## Deployment to Streamlit Cloud
1. Push this repository to GitHub.
2. Go to [Streamlit Cloud](https://share.streamlit.io/).
3. Connect your GitHub repository.
4. Set the Main file path to `app/main.py`.
5. Under "Advanced settings" -> "Secrets", copy the contents of your `.streamlit/secrets.toml` file.
6. Click Deploy!
