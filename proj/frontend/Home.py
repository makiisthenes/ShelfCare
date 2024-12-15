
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
import os
# os.chdir("C:\Fast Coding Projects [Memory Critical]\GemmaCompetitionProcurementManagement")
import streamlit as st
from proj.chain.lc_agent import execute_agent_tools
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "C:\Fast Coding Projects [Memory Critical]\GemmaCompetitionProcurementManagement\proj\chain\secrets\gemma-competition-da8786b08cd5.json"


st.set_page_config(layout="wide")



# Chatbot page..
st.title("ShelfCare")
st.markdown("AI Powered Procurement Management for Pharmacies - VanishingGradients")
st.markdown("-----")


# Initialize chat history and context
if "messages" not in st.session_state:
    st.session_state.messages = []
if "context" not in st.session_state:
    st.session_state.context = []


# Main Streamlit UI
with st.chat_message("system"):
    st.write("Welcome to the Procurement Management System.")
    st.write("Example questions include, 'Are any of my medicines going out of date?' \n'What stock is running low?'\n'Create new order for Paracetamol, quantity 500'")


# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

prompt = st.chat_input("Please enter your prompt here:")

if prompt:
    # Add user input to messages
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Process the prompt with chat history
    with st.spinner("Processing your request..."):
        response = execute_agent_tools(prompt, st.session_state.chat_history)

    # Update chat history
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    st.session_state.chat_history.append({"role": "assistant", "content": response['output']})

    # Add assistant's response to messages
    with st.chat_message("assistant"):
        st.markdown(response['output'])
    st.session_state.messages.append({"role": "assistant", "content": response['output']})