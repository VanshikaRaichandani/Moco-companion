print("new database.py loaded")
import sqlite3

DB_NAME = "moco.db"


def get_connection():
    """Create a connection to the SQLite database."""
    return sqlite3.connect(DB_NAME)


def create_tables():
    """Create conversations and messages tables."""
    conn = get_connection()
    cursor = conn.cursor()

    # Conversations table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT DEFAULT 'New Conversation',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Messages table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (conversation_id) REFERENCES conversations(id)
        )
    """)

    conn.commit()
    conn.close()


def create_conversation(title="New Conversation"):
    """Create a new conversation and return its ID."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO conversations (title)
        VALUES (?)
        """,
        (title,)
    )

    conversation_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return conversation_id


def update_conversation_title(conversation_id, title):
    """Update the title of a conversation."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE conversations
        SET title = ?
        WHERE id = ?
        """,
        (title, conversation_id)
    )

    conn.commit()
    conn.close()


def save_message(conversation_id, role, content):
    """Save a message to a specific conversation."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO messages (conversation_id, role, content)
        VALUES (?, ?, ?)
        """,
        (conversation_id, role, content),
    )

    conn.commit()
    conn.close()


def load_messages(conversation_id):
    """Load all messages for a specific conversation."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT role, content
        FROM messages
        WHERE conversation_id = ?
        ORDER BY id
        """,
        (conversation_id,),
    )

    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "role": role,
            "content": content
        }
        for role, content in rows
    ]


def clear_messages(conversation_id):
    """Delete all messages in a conversation."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        DELETE FROM messages
        WHERE conversation_id = ?
        """,
        (conversation_id,),
    )

    conn.commit()
    conn.close()

def delete_conversation(conversation_id):
    """Delete a conversation and all of its messages."""
    conn = get_connection()
    cursor = conn.cursor()

    # Delete messages belonging to the conversation
    cursor.execute(
        """
        DELETE FROM messages
        WHERE conversation_id = ?
        """,
        (conversation_id,),
    )

    # Delete the conversation itself
    cursor.execute(
        """
        DELETE FROM conversations
        WHERE id = ?
        """,
        (conversation_id,),
    )

    conn.commit()
    conn.close()

def get_conversations():
    """Return all conversations ordered by newest first."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, title
        FROM conversations
        ORDER BY created_at DESC, id DESC
    """)

    conversations = cursor.fetchall()

    conn.close()

    return conversations