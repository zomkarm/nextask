"""
nextask/db.py
All database operations.
Database: ~/.local/share/nextask/nextask.db
Schema:
  tasks — id, name, created_at, position
  items — id, task_id, text, completed, skipped, position
"""

import os
import sqlite3
from datetime import datetime

DB_DIR  = os.path.expanduser("~/.local/share/nextask")
DB_PATH = os.path.join(DB_DIR, "nextask.db")


class Database:

    def __init__(self):
        os.makedirs(DB_DIR, exist_ok=True)
        self.conn = sqlite3.connect(DB_PATH)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        self._create_tables()

    def _create_tables(self):
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS tasks (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                name       TEXT NOT NULL,
                created_at TEXT NOT NULL,
                position   INTEGER NOT NULL DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS items (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id   INTEGER NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
                text      TEXT NOT NULL,
                completed INTEGER NOT NULL DEFAULT 0,
                skipped   INTEGER NOT NULL DEFAULT 0,
                position  INTEGER NOT NULL DEFAULT 0
            );

            CREATE INDEX IF NOT EXISTS idx_items_task
                ON items(task_id, position);
        """)
        self.conn.commit()

    # ── Tasks ─────────────────────────────────

    def get_all_tasks(self) -> list:
        """Return all tasks ordered by position."""
        cur = self.conn.execute(
            "SELECT * FROM tasks ORDER BY position ASC, created_at ASC"
        )
        return cur.fetchall()

    def get_task(self, task_id: int):
        cur = self.conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        return cur.fetchone()

    def add_task(self, name: str) -> int:
        """Insert a new task. Returns new task id."""
        now = datetime.now().isoformat(timespec="seconds")
        # Position = current max + 1
        cur = self.conn.execute("SELECT COALESCE(MAX(position), -1) FROM tasks")
        pos = cur.fetchone()[0] + 1
        cur = self.conn.execute(
            "INSERT INTO tasks (name, created_at, position) VALUES (?, ?, ?)",
            (name.strip(), now, pos),
        )
        self.conn.commit()
        return cur.lastrowid

    def update_task_name(self, task_id: int, name: str):
        self.conn.execute(
            "UPDATE tasks SET name = ? WHERE id = ?",
            (name.strip(), task_id),
        )
        self.conn.commit()

    def delete_task(self, task_id: int):
        """Delete task and all its items (cascade)."""
        self.conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        self.conn.commit()

    def reorder_tasks(self, task_ids: list[int]):
        """Update position of tasks given ordered list of ids."""
        for pos, tid in enumerate(task_ids):
            self.conn.execute(
                "UPDATE tasks SET position = ? WHERE id = ?", (pos, tid)
            )
        self.conn.commit()

    # ── Items ─────────────────────────────────

    def get_items(self, task_id: int) -> list:
        """Return all items for a task ordered by position."""
        cur = self.conn.execute(
            "SELECT * FROM items WHERE task_id = ? ORDER BY position ASC",
            (task_id,),
        )
        return cur.fetchall()

    def get_current_item(self, task_id: int):
        """
        Return the current active item — first non-completed, non-skipped.
        If all remaining are skipped, reset skipped flags and return first.
        Returns None if all items are completed.
        """
        items = self.get_items(task_id)

        # Find first non-completed, non-skipped
        for item in items:
            if not item["completed"] and not item["skipped"]:
                return item

        # All remaining incomplete items are skipped — reset skipped flags
        incomplete = [i for i in items if not i["completed"]]
        if not incomplete:
            return None  # all done

        for item in incomplete:
            self.conn.execute(
                "UPDATE items SET skipped = 0 WHERE id = ?", (item["id"],)
            )
        self.conn.commit()

        # Return first incomplete after reset
        cur = self.conn.execute(
            """SELECT * FROM items
               WHERE task_id = ? AND completed = 0
               ORDER BY position ASC LIMIT 1""",
            (task_id,),
        )
        return cur.fetchone()

    def add_item(self, task_id: int, text: str) -> int:
        """Append a new item to the task. Returns new item id."""
        cur = self.conn.execute(
            "SELECT COALESCE(MAX(position), -1) FROM items WHERE task_id = ?",
            (task_id,),
        )
        pos = cur.fetchone()[0] + 1
        cur = self.conn.execute(
            "INSERT INTO items (task_id, text, position) VALUES (?, ?, ?)",
            (task_id, text.strip(), pos),
        )
        self.conn.commit()
        return cur.lastrowid

    def add_items_bulk(self, task_id: int, lines: list[str]):
        """Add multiple items preserving order."""
        cur = self.conn.execute(
            "SELECT COALESCE(MAX(position), -1) FROM items WHERE task_id = ?",
            (task_id,),
        )
        start_pos = cur.fetchone()[0] + 1
        for i, line in enumerate(lines):
            text = line.strip()
            if text:
                self.conn.execute(
                    "INSERT INTO items (task_id, text, position) VALUES (?, ?, ?)",
                    (task_id, text, start_pos + i),
                )
        self.conn.commit()

    def complete_item(self, item_id: int):
        self.conn.execute(
            "UPDATE items SET completed = 1, skipped = 0 WHERE id = ?",
            (item_id,),
        )
        self.conn.commit()

    def skip_item(self, item_id: int, task_id: int):
        """
        Mark item as skipped. It moves to end of incomplete items logically
        by setting skipped=1. get_current_item() handles the ordering.
        """
        self.conn.execute(
            "UPDATE items SET skipped = 1 WHERE id = ?", (item_id,)
        )
        self.conn.commit()

    def update_item_text(self, item_id: int, text: str):
        self.conn.execute(
            "UPDATE items SET text = ? WHERE id = ?",
            (text.strip(), item_id),
        )
        self.conn.commit()

    def delete_item(self, item_id: int):
        self.conn.execute("DELETE FROM items WHERE id = ?", (item_id,))
        self.conn.commit()

    def reorder_items(self, item_ids: list[int]):
        for pos, iid in enumerate(item_ids):
            self.conn.execute(
                "UPDATE items SET position = ? WHERE id = ?", (pos, iid)
            )
        self.conn.commit()

    # ── Progress ──────────────────────────────

    def get_progress(self, task_id: int) -> tuple[int, int]:
        """Return (completed_count, total_count)."""
        cur = self.conn.execute(
            "SELECT COUNT(*) FROM items WHERE task_id = ?", (task_id,)
        )
        total = cur.fetchone()[0]
        cur = self.conn.execute(
            "SELECT COUNT(*) FROM items WHERE task_id = ? AND completed = 1",
            (task_id,),
        )
        done = cur.fetchone()[0]
        return done, total

    def close(self):
        self.conn.close()