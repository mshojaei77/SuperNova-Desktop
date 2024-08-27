import sqlite3

class DatabaseService:
    def __init__(self):
        self.conn = sqlite3.connect("chat_history.db")
        self.cursor = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        """Create necessary tables."""
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS chats
                               (id INTEGER PRIMARY KEY AUTOINCREMENT,
                                title TEXT,
                                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS messages
                               (id INTEGER PRIMARY KEY AUTOINCREMENT,
                                chat_id INTEGER,
                                role TEXT,
                                content TEXT,
                                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                FOREIGN KEY (chat_id) REFERENCES chats (id))''')
        self.conn.commit()

    def execute_query(self, query, params=()):
        """Execute a query."""
        self.cursor.execute(query, params)
        self.conn.commit()

    def fetch_all(self, query, params=()):
        """Fetch all results from a query."""
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def create_new_chat(self, title):
        """Create a new chat session."""
        self.execute_query("INSERT INTO chats (title) VALUES (?)", (title,))
        return self.cursor.lastrowid

    def load_chat_history(self):
        """Load chat history."""
        return self.fetch_all("SELECT id, title FROM chats ORDER BY created_at DESC")

    def load_chat_messages(self, chat_id):
        """Load messages for a specific chat."""
        return self.fetch_all("SELECT role, content FROM messages WHERE chat_id = ? ORDER BY created_at ASC", (chat_id,))

    def save_message(self, chat_id, role, content):
        """Save a message to the database."""
        self.execute_query("INSERT INTO messages (chat_id, role, content) VALUES (?, ?, ?)", (chat_id, role, content))

    def clear_conversations(self):
        """Clear all conversations."""
        self.execute_query("DELETE FROM messages")
        self.execute_query("DELETE FROM chats")

    def close(self):
        """Close the database connection."""
        self.conn.close()
