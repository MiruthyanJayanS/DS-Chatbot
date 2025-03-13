import streamlit as st
import uuid
import os
import json
import pymysql
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, MetaData, Table, inspect
from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory

load_dotenv()
pymysql.install_as_MySQLdb()

def get_api_key():
    return os.getenv("API_KEY") or st.secrets["API_KEY"]

def get_database_url():
    return os.getenv("RAILWAY_DATABASE_URL") or st.secrets["RAILWAY_DATABASE_URL"]

DATABASE_URL = get_database_url()
engine = create_engine(DATABASE_URL)

metadata = MetaData()
message_store = Table(
    "message_store", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("session_id", String, nullable=False),
    Column("message", String, nullable=False)
)

inspector = inspect(engine)
if not inspector.has_table("message_store"):
    metadata.create_all(engine)

USER_DATA_FILE = "user_data.json"

def save_user_data(name, user_id):
    try:
        users = {}
        if os.path.exists(USER_DATA_FILE):
            with open(USER_DATA_FILE, "r") as f:
                users = json.load(f)
        users[name] = user_id
        with open(USER_DATA_FILE, "w") as f:
            json.dump(users, f)
    except Exception as e:
        st.error(f"Error saving user data: {e}")

def get_user_id(name):
    try:
        if os.path.exists(USER_DATA_FILE):
            with open(USER_DATA_FILE, "r") as f:
                users = json.load(f)
            return users.get(name)
    except Exception as e:
        st.error(f"Error loading user data: {e}")
    return None

def setup_chat_model(api_key):
    return ChatGoogleGenerativeAI(
        api_key=api_key, model="gemini-1.5-pro", temperature=0.7
    )

def get_session_message_history(session_id):
    return SQLChatMessageHistory(session_id=session_id, connection=engine)

def chat_prompt_template():
    return ChatPromptTemplate(
        messages=[
            ("system", """You are a knowledgeable and engaging AI assistant specializing in Data Science.
             Your role is to serve as a dedicated Data Science tutor, answering only Data Science-related queries. 
             If a user asks about their name, respond with '{user_name} is your name!'. Keep responses clear, accurate, 
             and tailored to the user's understanding level. If a query falls outside Data Science, politely redirect the user back to relevant topics. 
             Maintain a friendly and professional tone while providing insightful explanations, examples, and guidance.
             If users ask for additional learning materials, suggest resources like online courses, research papers, 
             official documentation (such as Scikit-Learn or TensorFlow), and practical platforms like Kaggle for hands-on experience, 
             without directly linking to them. Ensure explanations are practical, engaging, and backed by examples."""), 
            MessagesPlaceholder(variable_name="history"),
            ("human", "{human_input}")
        ]
    )

output_parser = StrOutputParser()
api_key = get_api_key()
chat_model = setup_chat_model(api_key)
chat_template = chat_prompt_template()
chat_chain = chat_template | chat_model | output_parser

def conversation_chain_creation():
    return RunnableWithMessageHistory(
        chat_chain,
        get_session_message_history,
        input_messages_key="human_input",
        history_messages_key="history"
    )

conversation_chain = conversation_chain_creation()

def chat_bot(prompt, user_id):
    if not prompt:
        return "Please enter a message."

    config = {"configurable": {"session_id": user_id}}
    input_prompt = {"user_name": st.session_state["user_name"], "human_input": prompt}
    response_container = st.empty()
    response = conversation_chain.invoke(input_prompt, config=config)


    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []
    st.session_state["chat_history"].append(("human", prompt))
    st.session_state["chat_history"].append(("ai", response))

    return response

def fetch_past_chats(user_id):
    chat_history = get_session_message_history(user_id)
    messages = chat_history.messages

    formatted_messages = []
    for msg in messages:
        role = "human" if msg.type == "human" else "ai"
        formatted_messages.append((role, msg.content))

    return formatted_messages

st.set_page_config(page_title="DataScience Chatbot", layout="wide")
st.title("📊 DataScience Chatbot")

def sidebar():
    with st.sidebar:
        st.header("User Login")
        st.subheader("Retrieve previous chat session or start a new one.")

        if "user_name" not in st.session_state:
            st.session_state["user_name"] = None
        if "user_id" not in st.session_state:
            st.session_state["user_id"] = None
        if "chat_history" not in st.session_state:
            st.session_state["chat_history"] = []

        choice = st.radio("Choose an option:", ["New User ID", "Existing User ID"])

        if choice == "New User ID":
            user_name = st.text_input("Enter your name", key="new_user_input", placeholder="Make it unique")
            if st.button("Start Chat") and user_name:
                user_id = str(uuid.uuid4())
                st.session_state["user_name"] = user_name
                st.session_state["user_id"] = user_id
                save_user_data(user_name, user_id)
                st.session_state["chat_history"] = []
                st.success(f"Welcome, {user_name}! Your session has started.")

        elif choice == "Existing User ID":
            user_name = st.text_input("Enter your name", key="existing_user_input", placeholder="Enter name", type="password")
            if st.button("Retrieve Session") and user_name:
                user_id = get_user_id(user_name)
                if user_id:
                    st.session_state["user_name"] = user_name
                    st.session_state["user_id"] = user_id
                    past_messages = fetch_past_chats(user_id)
                    st.session_state["chat_history"] = past_messages
                    st.success(f"Welcome back, {user_name}! Resuming session.")
                else:
                    st.error("No session found. Try creating a new one.")

sidebar()

if "user_name" in st.session_state and st.session_state["user_name"]:
    user_name = st.session_state["user_name"]
    user_id = st.session_state["user_id"]

    st.chat_message("ai", avatar="🤖").write(f"Hello, {user_name}! How can I assist you today?")

    for sender, message in st.session_state["chat_history"]:
        with st.chat_message(sender, avatar="🤖" if sender == "ai" else "👤"):
            st.write(message)

    input_prompt = st.chat_input(placeholder="Type your question here...")

    if input_prompt:
        with st.chat_message("human", avatar="👤"):
            st.write(input_prompt)

        # response = chat_bot(input_prompt, user_id)    
        with st.chat_message("ai", avatar="🤖"):
            response_container = st.empty()  # Placeholder for streaming  
            response = ""
            for chunk in chat_bot(input_prompt, user_id):  # Assuming chat_bot() returns an iterable
                response += chunk
                response_container.write(response)
