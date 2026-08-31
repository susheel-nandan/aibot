import streamlit as st
import google.generativeai as genai
import os

api_key = st.secrets.get("GEMINI_API_KEY")
genai.configure(api_key=api_key)

with open("models.txt", "w") as f:
    for m in genai.list_models():
        f.write(f"{m.name} - {m.supported_generation_methods}\n")
st.write("Done")
