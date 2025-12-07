"""Human review queue repository."""

import sqlite3
from typing import List, Dict, Any, Optional
from datetime import datetime
import json


class HumanReviewRepository:
    """Repository for managing human review queue."""
    
    def __init__(self, db_path: str = "./demo.db"):
        """
        Initialize human review repository.
        
        Args:
            db_path: SQLite database path
        """
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize database tables."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create human_review_queue table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS human_review_queue (
                checkpoint_id TEXT PRIMARY KEY,
                invoice_id TEXT NOT NULL,
                vendor_name TEXT NOT NULL,
                amount REAL NOT NULL,
                created_at TEXT NOT NULL,
                reason_for_hold TEXT NOT NULL,
                mismatch_reason TEXT,
                failed_stage TEXT,
                review_url TEXT NOT NULL,
                state_blob TEXT,
                thread_id TEXT,
                decision TEXT,
                reviewer_id TEXT,
                notes TEXT,
                updated_at TEXT
            )
        """)
        
        # Add new columns if they don't exist (for existing databases)
        cursor.execute("PRAGMA table_info(human_review_queue)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if "mismatch_reason" not in columns:
            cursor.execute("ALTER TABLE human_review_queue ADD COLUMN mismatch_reason TEXT")
        if "failed_stage" not in columns:
            cursor.execute("ALTER TABLE human_review_queue ADD COLUMN failed_stage TEXT")
        
        conn.commit()
        conn.close()
    
    def save_checkpoint(self, checkpoint_data: Dict[str, Any]):
        """
        Save checkpoint to human review queue.
        
        Args:
            checkpoint_data: Checkpoint data dict
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO human_review_queue 
            (checkpoint_id, invoice_id, vendor_name, amount, created_at, 
             reason_for_hold, mismatch_reason, failed_stage, review_url, state_blob, thread_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            checkpoint_data["checkpoint_id"],
            checkpoint_data["invoice_id"],
            checkpoint_data["vendor_name"],
            checkpoint_data["amount"],
            checkpoint_data["created_at"],
            checkpoint_data["reason_for_hold"],
            checkpoint_data.get("mismatch_reason"),
            checkpoint_data.get("failed_stage"),
            checkpoint_data["review_url"],
            checkpoint_data.get("state_blob"),
            checkpoint_data.get("thread_id")
        ))
        
        conn.commit()
        conn.close()
    
    def get_pending_reviews(self) -> List[Dict[str, Any]]:
        """
        Get all pending reviews (without decision).
        
        Note: This method only checks the database. The API endpoint should
        filter these results based on actual workflow state to ensure only
        truly paused workflows are returned.
        
        Returns:
            List of pending review items (candidates - need state verification)
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT checkpoint_id, invoice_id, vendor_name, amount, 
                   created_at, reason_for_hold, mismatch_reason, failed_stage, 
                   review_url, thread_id
            FROM human_review_queue
            WHERE decision IS NULL
            ORDER BY created_at DESC
        """)
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_checkpoint(self, checkpoint_id: str) -> Optional[Dict[str, Any]]:
        """
        Get checkpoint by ID.
        
        Args:
            checkpoint_id: Checkpoint ID
            
        Returns:
            Checkpoint data or None
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM human_review_queue
            WHERE checkpoint_id = ?
        """, (checkpoint_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        return dict(row) if row else None
    
    def update_decision(
        self,
        checkpoint_id: str,
        decision: str,
        reviewer_id: str,
        notes: Optional[str] = None
    ):
        """
        Update checkpoint with human decision.
        
        Args:
            checkpoint_id: Checkpoint ID
            decision: Decision (ACCEPT/REJECT)
            reviewer_id: Reviewer ID
            notes: Optional notes
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE human_review_queue
            SET decision = ?, reviewer_id = ?, notes = ?, updated_at = ?
            WHERE checkpoint_id = ?
        """, (
            decision,
            reviewer_id,
            notes,
            datetime.utcnow().isoformat(),
            checkpoint_id
        ))
        
        conn.commit()
        conn.close()
    
    def get_state_blob(self, checkpoint_id: str) -> Optional[Dict[str, Any]]:
        """
        Get state blob from checkpoint.
        
        Args:
            checkpoint_id: Checkpoint ID
            
        Returns:
            State dict or None
        """
        checkpoint = self.get_checkpoint(checkpoint_id)
        if not checkpoint or not checkpoint.get("state_blob"):
            return None
        
        try:
            state_data = json.loads(checkpoint["state_blob"])
            return state_data.get("workflow_state")
        except json.JSONDecodeError:
            return None

