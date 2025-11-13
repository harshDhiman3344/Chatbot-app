from dotenv import load_dotenv
import streamlit as st
import os
from langchain_google_genai import ChatGoogleGenerativeAI

#loading the env

load_dotenv()

#streamlit page setup

st.set_page_config(
    page_title="chatbot",
    layout="centered"
)

st.title("Genai Chatbot")


#Chat history

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "llm" not in st.session_state:
    st.session_state.llm = None
if "llm_error" not in st.session_state:
    st.session_state.llm_error = None


#Show Chat History
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# Lazy-init LLM to avoid crashing the app when credentials are missing
def create_llm():
    try:
        # Use API key from environment variable
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        return ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=api_key
        )
    except Exception as e:
        # store the error so the Streamlit UI can show guidance
        st.session_state.llm_error = str(e)
        return None



user_prompt = st.chat_input("Enter your message...")

# If LLM failed to initialize earlier, show a friendly message with quick fixes
if st.session_state.llm_error:
    st.error("LLM initialization failed - check your GEMINI_API_KEY in the .env file")
    st.code("Make sure your .env file contains:\nGEMINI_API_KEY=your_actual_api_key_here", language='text')

if user_prompt:
    st.chat_message("user").markdown(user_prompt)
    st.session_state.chat_history.append({"role":"user","content":user_prompt})

    # ensure LLM exists (create lazily)
    if st.session_state.llm is None:
        st.session_state.llm = create_llm()

    if st.session_state.llm is None:
        # still None -> show error message in chat and don't crash
        err_msg = st.session_state.llm_error or "LLM could not be initialized."
        st.chat_message("assistant").markdown("**Error initializing LLM:** " + err_msg)
        st.session_state.chat_history.append({"role":"assistant","content":"Error initializing LLM: " + err_msg})
    else:
        response = st.session_state.llm.invoke(
            input=[{"role":"system","content":"You are a helpful assistant"}, *st.session_state.chat_history]
        )
        assistant_response = response.content
        st.chat_message("assistant").markdown(assistant_response)
        st.session_state.chat_history.append({"role":"assistant","content":assistant_response})