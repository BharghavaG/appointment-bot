import streamlit as st
import threading
import time
import os
from dotenv import load_dotenv

# Load env variables before importing modules that need them
load_dotenv()

# We only import these after checking for required config
try:
    from audio_io import record_audio_until_silence, play_audio_from_text
    from llm_agent import LLMAgent, transcribe_audio
    from calendar_service import get_calendar_service
except Exception as e:
    st.error(f"Failed to load modules. Did you install dependencies? Error: {e}")

st.set_page_config(page_title="Dentist Appointment Bot", page_icon="🦷")

st.title("🦷 Voice-Based Dentist Appointment Bot")

# Ensure API keys are set
groq_api_key = os.environ.get("GROQ_API_KEY")
if not groq_api_key:
    st.warning("Please set the `GROQ_API_KEY` environment variable in a `.env` file.")
    st.stop()

if "agent" not in st.session_state:
    st.session_state.agent = LLMAgent()

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "listening_active" not in st.session_state:
    st.session_state.listening_active = False

def add_message(role, text):
    st.session_state.chat_history.append({"role": role, "content": text})

# Display Chat History
chat_container = st.container()
with chat_container:
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Log in to Google Calendar"):
        try:
            service = get_calendar_service()
            if service:
                st.success("Successfully logged into Google Calendar!")
        except Exception as e:
            st.error(f"Login failed: {e}")

with col2:
    if st.button("Start Voice Assistant"):
        st.session_state.listening_active = True
        st.rerun()

with col3:
    if st.button("Stop"):
        st.session_state.listening_active = False
        st.rerun()

status_text = st.empty()

if st.session_state.listening_active:
    # We are in the active loop
    
    # Check if this is the very first turn. If so, speak the greeting first!
    if not st.session_state.chat_history:
        greeting = "Hello, welcome to ABC Dental Hospital. How can I help you today?"
        add_message("assistant", greeting)
        
        with chat_container:
            with st.chat_message("assistant"):
                st.write(greeting)
        
        status_text.success("Speaking initial greeting...")
        play_audio_from_text(greeting)
    
    status_text.info("Listening... Speak now.")
    
    # 1. Record Audio
    audio_file = record_audio_until_silence()
    
    if audio_file:
        status_text.warning("Processing audio...")
        # 2. Transcribe
        user_text = transcribe_audio(audio_file)
        
        if user_text.strip():
            add_message("user", user_text)
            
            # Display user message immediately
            with chat_container:
                with st.chat_message("user"):
                    st.write(user_text)
                    
            status_text.warning("Thinking...")
            
            # 3. Get LLM Response (might include tool calls)
            bot_text = st.session_state.agent.process_message(user_text)
            
            add_message("assistant", bot_text)
            
            # Display bot message
            with chat_container:
                with st.chat_message("assistant"):
                    st.write(bot_text)
            
            status_text.success("Speaking...")
            
            # 4. Play Audio Response
            play_audio_from_text(bot_text)
            
        try:
            os.remove(audio_file)
        except:
            pass

    # Rerun to listen again automatically
    time.sleep(0.5)
    st.rerun()
