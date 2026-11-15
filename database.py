import sqlite3
import os

DB_PATH = os.path.join(
    os.path.dirname(__file__),
    "datapulse.db"
)


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS dataset_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                dataset_name TEXT NOT NULL,
                file_path TEXT NOT NULL,
                upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                total_rows INTEGER DEFAULT 0,
                total_columns INTEGER DEFAULT 0
            )
        """)
        conn.commit()


def save_dataset(name, file_path, rows, columns):
    with get_connection() as conn:
        cursor = conn.execute("""
            INSERT INTO dataset_history
            (dataset_name, file_path, total_rows, total_columns)
            VALUES (?, ?, ?, ?)
        """, (
            name,
            file_path,
            int(rows),
            int(columns)
        ))

        conn.commit()
        return cursor.lastrowid


def get_dataset_history():
    with get_connection() as conn:
        records = conn.execute("""
            SELECT *
            FROM dataset_history
            ORDER BY upload_date DESC, id DESC
        """).fetchall()

        return records


def get_dataset_by_id(dataset_id):
    with get_connection() as conn:
        record = conn.execute("""
            SELECT *
            FROM dataset_history
            WHERE id = ?
        """, (dataset_id,)).fetchone()

        return record


def delete_dataset(dataset_id):

    conn = get_connection()

    try:
        record = conn.execute("""
            SELECT file_path
            FROM dataset_history
            WHERE id = ?
        """, (dataset_id,)).fetchone()

        if record is None:
            print(f"Dataset ID {dataset_id} not found.")
            return None

        cursor = conn.execute("""
            DELETE FROM dataset_history
            WHERE id = ?
        """, (dataset_id,))

        conn.commit()

        if cursor.rowcount == 1:
            print(f"Dataset ID {dataset_id} deleted successfully.")
            return record["file_path"]

        return None

    except sqlite3.Error as error:
        conn.rollback()
        print("Database delete error:", error)
        return None

    finally:
        conn.close()


def clear_dataset_history():
    with get_connection() as conn:
        conn.execute("DELETE FROM dataset_history")
        conn.commit()