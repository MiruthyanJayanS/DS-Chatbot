from sqlalchemy import create_engine, Column, Integer, String, MetaData, Table
from sqlalchemy.exc import OperationalError

# Database Connection
DATABASE_URL = "sqlite:///chats_data.sqlite"
engine = create_engine(DATABASE_URL)
metadata = MetaData()

# Define Table Schema
message_store = Table(
    "message_store", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("session_id", String, nullable=False),
    Column("message", String, nullable=False)
)

# Function to Create Table if it doesn't exist
def create_db():
    try:
        metadata.create_all(engine)
        print("Database initialized successfully!")
    except OperationalError as e:
        print(f"Database Error: {e}")

# Call the function to initialize the database
if __name__ == "__main__":
    create_db()
