import streamlit as st
import sys
import os
from datetime import datetime

import requests

# Backend URL Configuration
# Default to local for development, override with env var in production (Railway)
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# Page Configuration
st.set_page_config(
    page_title="HDFC Mutual Fund Assistant",
    page_icon="💬",
    layout="centered"
)

# Professional Custom CSS for Conversational Chat
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stChatInputContainer {
        padding-bottom: 20px;
    }
    .disclaimer {
        font-size: 0.8rem;
        color: #6c757d;
        text-align: center;
        padding: 10px;
        border-top: 1px solid #dee2e6;
        margin-top: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# Header Section
st.title("💬 HDFC Mutual Fund Assistant")
st.caption("Your official conversational guide to HDFC Mutual Fund facts.")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

def ask_backend(prompt, history):
    try:
        response = requests.post(
            f"{BACKEND_URL}/ask",
            json={"prompt": prompt, "chat_history": history},
            timeout=30
        )
        if response.status_code == 200:
            return response.json().get("response", "No response from assistant.")
        else:
            return f"Error: Backend returned status {response.status_code}. {response.text}"
    except Exception as e:
        return f"Error connecting to backend: {e}"


# Sidebar / Persistent Disclaimer
with st.sidebar:
    st.header("Assistance Policy")
    st.info("**Facts-Only Mode**\nI provide factual details from official HDFC, AMFI, and SEBI sources.")
    st.warning("**No Investment Advice**\nI do not recommend funds or calculate future returns.")
    
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.rerun()
        
    st.divider()
    st.caption(f"Knowledge Base Version: {datetime.now().strftime('%Y-%m-%d')}")

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])



# React to user input
if prompt := st.chat_input("Ask me anything about HDFC Mutual Funds..."):
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Process history to pass to engine
    # We pass the history *before* adding the new prompt to avoid recursion
    chat_history = st.session_state.messages.copy()
    
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            # Pass the query and history to the backend API
            response = ask_backend(prompt, chat_history)
            st.markdown(response)

    
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})
    
    # Rerun to clear input and update display
    st.rerun()

# Footer
st.markdown("""
    <div class="disclaimer">
        Official Factual Information Service. No Investment Advice. <br>
        Source: HDFC Mutual Fund / AMFI / SEBI.
    </div>
    """, unsafe_allow_html=True)
