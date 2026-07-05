#!/usr/bin/env python3
"""
Database migration: add chat_messages.metadata_json so an assistant message can
carry structured data (e.g. clickable interview time-slot options) alongside
its plain-text content.
"""
import sqlite3
import os


def _db_path() -> str:
    database_url = os.getenv("DATABASE_URL", "sqlite:///interview_system.db")
    if database_url.startswith("sqlite:///"):
        return database_url[10:]
    return database_url


def migrate_database():
    database_path = _db_path()
    print(f"Migrating database: {database_path}")

    try:
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()

        cursor.execute("PRAGMA table_info(chat_messages)")
        columns = [c[1] for c in cursor.fetchall()]
        if 'metadata_json' not in columns:
            cursor.execute("ALTER TABLE chat_messages ADD COLUMN metadata_json TEXT")
            print("✅ Added chat_messages.metadata_json")
        else:
            print("✅ chat_messages.metadata_json already exists")

        conn.commit()
        conn.close()
        print("✅ Database migration completed successfully")

    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

    return True


if __name__ == "__main__":
    migrate_database()
