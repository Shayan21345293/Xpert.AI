import streamlit as st
import google.generativeai as genai

# Load API key from Streamlit secrets
api_key = st.secrets.get("GEMINI_API_KEY")

# Setup
if not api_key:
    st.error("Gemini API key not found. Please add it to .streamlit/secrets.toml")
    st.stop()

genai.configure(api_key=api_key)
model = genai.GenerativeModel("models/gemini-1.5-flash")

# UI Title
st.title("🤖 Xpert.AI Chat with Gemini")

# Session state for chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Display chat history
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User input
if prompt := st.chat_input("Type your message..."):
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        response = model.generate_content(prompt)
        reply = response.text
    except Exception as e:
        reply = "❌ Error from Gemini API: " + str(e)

    st.session_state.chat_history.append({"role": "assistant", "content": reply})
    with st.chat_message("assistant"):
        st.markdown(reply)
