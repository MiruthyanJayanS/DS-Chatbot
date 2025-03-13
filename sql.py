import pymysql
from sqlalchemy import create_engine, Column, Integer, String, MetaData, text
from sqlalchemy.orm import declarative_base, sessionmaker
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Ensure PyMySQL is used as MySQLdb alternative
pymysql.install_as_MySQLdb()

# Define the MySQL Database URL
DATABASE_URL = os.getenv("RAILWAY_DATABASE_URL")

# Create Engine
engine = create_engine(DATABASE_URL, echo=True)

# Define Metadata and ORM Base
metadata = MetaData()
Base = declarative_base()

# Define Table Schema
class MessageStore(Base):
    __tablename__ = 'message_store'

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(255), nullable=False)
    message = Column(String(1000), nullable=False)

# Create Table if Not Exists
def create_table():
    Base.metadata.create_all(engine)
    print("✅ Database table 'message_store' created successfully.")

# Establish Session
SessionLocal = sessionmaker(bind=engine)

def get_db_session():
    return SessionLocal()

# Function to DELETE all rows and reset AUTO_INCREMENT
def reset_table():
    with engine.connect() as connection:
        try:
            # Step 1: Delete all rows
            connection.execute(text("DELETE FROM message_store"))
            
            # Step 2: Reset AUTO_INCREMENT to start from 1
            connection.execute(text("ALTER TABLE message_store AUTO_INCREMENT = 1"))

            print("✅ Table cleared, and ID auto-increment reset to 1.")
        except Exception as e:
            print(f"❌ Error resetting table: {e}")


# Interactive Menu for Dynamic Execution
def main():
    create_table()  # Ensures the table is created before other operations

    while True:
        print("\nChoose an option:")
        print("1. Reset table (delete all rows & reset auto-increment)")
        print("2. Exit")

        choice = input("Enter your choice (1/2): ").strip()

        if choice == "1":
            reset_table()
        elif choice == "2":
            print("Exiting...")
            break
        else:
            print("❌ Invalid choice. Please enter 1 or 2.")

# Run Script
if __name__ == "__main__":
    main()
