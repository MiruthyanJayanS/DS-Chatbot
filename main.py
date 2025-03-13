from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.messages import HumanMessage, AIMessage
import uuid
import streamlit as st
from dotenv import load_dotenv
import os
import json

# Load environment variables
load_dotenv()

# Load API key
def get_api_key():
    api_key = os.getenv('API_KEY') or st.secrets["API_KEY"]
    if not api_key:
        st.error("API Key not found! Please set it in the .env file.")
        st.stop()
    return api_key

# Initialize Streamlit app
st.set_page_config(page_title="DataScience Chatbot", layout="wide")
st.title("📊 DataScience Chatbot")

# File to store user UUIDs
USER_DATA_FILE = "user_data.json"

# Function to store user details in a JSON file
def save_user_data(name, user_id):
    try:
        if os.path.exists(USER_DATA_FILE):
            with open(USER_DATA_FILE, "r") as f:
                users = json.load(f)
        else:
            users = {}

        users[name] = user_id

        with open(USER_DATA_FILE, "w") as f:
            json.dump(users, f)
    except Exception as e:
        st.error(f"Error saving user data: {e}")

# Function to retrieve user UUID based on name
def get_user_id(name):
    try:
        if os.path.exists(USER_DATA_FILE):
            with open(USER_DATA_FILE, "r") as f:
                users = json.load(f)
            return users.get(name)
    except Exception as e:
        st.error(f"Error loading user data: {e}")
    return None

# Setup chatbot components
def setup_chat_model(api_key):
    return ChatGoogleGenerativeAI(
        api_key=api_key, 
        model="gemini-1.5-pro", 
        temperature=0.7
    )

def get_session_message_history_from_db(session_id):
    return SQLChatMessageHistory(
        session_id=session_id, 
        connection="sqlite:///chats_data.sqlite"
    )

def chat_prompt_template():
    return ChatPromptTemplate(
        messages=[
            ("system", "You are a helpful AI assistant specializing in Data Science. Answer when user asks about my name {user_name} is their name!."),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{human_input}")
        ]
    )

def output_parsers():
    return StrOutputParser()

# Initialize chatbot
api_key = get_api_key()
output_parser = output_parsers()
chat_model = setup_chat_model(api_key)
chat_template = chat_prompt_template()
chat_chain = chat_template | chat_model | output_parser

def conversation_chain_creation():
    return RunnableWithMessageHistory(
        chat_chain,
        get_session_message_history_from_db,
        input_messages_key="human_input",
        history_messages_key="history"
    )

conversation_chain = conversation_chain_creation()

def chat_bot(prompt, user_id):
    if not prompt:
        return "Please enter a message."

    config = {"configurable": {"session_id": user_id}}
    input_prompt = {"user_name": user_name,"human_input": prompt}

    response = conversation_chain.invoke(input_prompt, config=config)
    return response

# Sidebar for user login
def sidebar():
    with st.sidebar:
        st.header("User Login")
        st.subheader("This is a unique chat session for each user. Try to remember your User ID for accessing the previous session.")
        if "user_name" not in st.session_state:
            st.session_state["user_name"] = None
        if "user_id" not in st.session_state:
            st.session_state["user_id"] = None

        choice = st.radio("Choose an option:", ["New User ID", "Existing User ID"])

        if choice == "New User ID":
            user_name = st.text_input("Enter your name", key="new_user_input", placeholder="Make it unique")
            if st.button("Start Chat") and user_name:
                user_id = str(uuid.uuid4())
                st.session_state["user_name"] = user_name
                st.session_state["user_id"] = user_id
                st.session_state["messages"] = []  # Initialize chat history
                save_user_data(user_name, user_id)  # Store user ID
                st.success(f"Welcome, {user_name}! Your session has started.")

        elif choice == "Existing User ID":
            user_name = st.text_input("Enter your name", key="existing_user_input", type="password", placeholder="Remember your User ID")
            if st.button("Retrieve Session") and user_name:
                user_id = get_user_id(user_name)
                if user_id:
                    st.session_state["user_name"] = user_name
                    st.session_state["user_id"] = user_id
                    
                    # 💡 FIX: Reset previous messages and load correct history
                    st.session_state["messages"] = get_session_message_history_from_db(user_id).messages
                    
                    st.success(f"Welcome back, {user_name}! Resuming session.")
                else:
                    st.error("No session found for this name. Try creating a new one.")

# Retrieve user details
sidebar()

# Display chat interface only if user is logged in
if "user_name" in st.session_state and "user_id" in st.session_state and st.session_state["user_name"] and st.session_state["user_id"]:
    user_name = st.session_state["user_name"]
    user_id = st.session_state["user_id"]

    st.chat_message("ai", avatar="🤖").write(f"Hello, {user_name}! I am a Data Science Chatbot. How can I assist you today?")

    # 💡 FIX: Correctly fetch and display previous chat messages
    if "messages" not in st.session_state or not st.session_state["messages"]:
        st.session_state["messages"] = get_session_message_history_from_db(user_id).messages

    # Display previous messages only for the current user
    for message in st.session_state["messages"]:
        if isinstance(message, HumanMessage):
            with st.chat_message("human", avatar="👤"):
                st.write(message.content)
        elif isinstance(message, AIMessage):
            with st.chat_message("ai", avatar="🤖"):
                st.write(message.content)

    # Chat input and response handling
    input_prompt = st.chat_input(placeholder="Type your question here...")
    
    if input_prompt:
        # Display user's message
        with st.chat_message("human", avatar="👤"):
            st.write(input_prompt)
        
        # Store user's message
        st.session_state["messages"].append(HumanMessage(content=input_prompt))

        # Get AI response
        response = chat_bot(input_prompt, user_id)
        
        # Display AI's response
        with st.chat_message("ai", avatar="🤖"):
            st.write(response)
        
        # Store AI's response
        st.session_state["messages"].append(AIMessage(content=response))