"""Checkpoint store using LangGraph SqliteSaver."""

from langgraph.checkpoint.sqlite import SqliteSaver
from typing import Optional
import os
import sqlite3


class CheckpointStore:
    """Wrapper around LangGraph SqliteSaver for checkpoint management."""
    
    def __init__(self, db_path: str = "sqlite:///./demo.db"):
        """
        Initialize checkpoint store.
        
        Args:
            db_path: SQLite database path
        """
        # Extract path from sqlite:/// URL
        if db_path.startswith("sqlite:///"):
            db_path = db_path.replace("sqlite:///", "")
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(db_path) if os.path.dirname(db_path) else ".", exist_ok=True)
        
        # Create checkpointer using direct initialization
        # SqliteSaver.from_conn_string returns a context manager, so we use SqliteSaver directly
        conn = sqlite3.connect(db_path, check_same_thread=False)
        self.checkpointer = SqliteSaver(conn)
        self.db_path = db_path
        self.conn = conn  # Keep connection alive
    
    def get_checkpointer(self):
        """Get LangGraph checkpointer instance."""
        return self.checkpointer

