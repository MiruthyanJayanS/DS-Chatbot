# Data Science Chatbot

## Overview
This project is a **Data Science Chatbot** built using **Streamlit** and **LangChain**, powered by Google's **Gemini** model. It provides an interactive chat interface for users to ask data science-related questions and retrieve previous chat histories using a **MySQL database**.

---

## Features
- User authentication with **unique session IDs**.
- **Persistent chat history** stored in a MySQL database.
- **Conversational AI tutor** focused on data science.
- **Streamlit UI** for easy interaction.
- **SQLAlchemy ORM** for database operations.

---

## Installation & Setup
### Prerequisites
Ensure you have the following installed:
- Python 3.8+
- MySQL Server
- Virtual Environment (recommended)

### Steps to Set Up the Project
1. **Clone the Repository**
   ```sh
   git clone <repository_url>
   cd chatbot-project
   ```
2. **Create a Virtual Environment**
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```
3. **Install Dependencies**
   ```sh
   pip install -r requirements.txt
   ```
4. **Set Up Environment Variables**
   - Create a `.env` file in the project root.
   - Add the following:
     ```env
     API_KEY=your_google_api_key
     RAILWAY_DATABASE_URL=mysql+pymysql://user:password@host/dbname
     ```
5. **Run the Application**
   ```sh
   streamlit run app.py
   ```

---

## Database Setup (Railway MySQL)
### Simple Steps for Railway Database Creation:
1. **Sign up at Railway.app** and create a new project.
2. **Add a MySQL database** as a service.
3. **Copy the database connection URL** provided by Railway.
4. **Update your `.env` file** with the copied `RAILWAY_DATABASE_URL`.
5. **Run the SQL handler script** to create necessary tables.
   ```sh
   python sql_handler.py
   ```
6. **Verify the table creation** using MySQL Workbench or any SQL client.

---

## Running SQL Handler
The `sql_handler.py` script ensures the **message_store** table is created and offers options to reset it.

1. Run the script:
   ```sh
   python sql_handler.py
   ```
2. Choose an option:
   - `1` to reset the table (delete all rows & reset auto-increment).
   - `2` to exit.

---

## Future Improvements
- Add support for more AI models.
- Enhance UI/UX with additional customization.
- Implement real-time chat streaming.
- Expand chatbot capabilities beyond data science.

---

## License
This project is **open-source** under the MIT License.

---

## Contributing
Pull requests are welcome! For major changes, please open an issue first to discuss proposed modifications.

