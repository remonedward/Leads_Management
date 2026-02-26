import sqlite3
import os
import pandas as pd
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_path="leads_database.db"):
        self.db_path = db_path
        self._initialize_db()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _sanitize_sql_name(self, name):
        """Sanitizes names for use as table or column identifiers in SQL."""
        return str(name).replace('[', '').replace(']', '').replace('"', '')

    def _initialize_db(self):
        """Initializes the basic tables if they don't exist."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # Leads table - will have dynamic columns added as needed
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS leads (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    import_date TEXT,
                    source_file TEXT
                )
            """)
            # Interactions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS interactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    lead_id INTEGER,
                    contact_date TEXT,
                    contact_time TEXT,
                    result TEXT,
                    notes TEXT,
                    FOREIGN KEY (lead_id) REFERENCES leads (id)
                )
            """)
            conn.commit()

    def add_column(self, table_name, column_name, column_type="TEXT"):
        """Adds a new column to a table if it doesn't already exist."""
        table_name = self._sanitize_sql_name(table_name)
        column_name = self._sanitize_sql_name(column_name)
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(f"PRAGMA table_info([{table_name}])")
                columns = [info[1] for info in cursor.fetchall()]

                if column_name not in columns:
                    cursor.execute(f"ALTER TABLE [{table_name}] ADD COLUMN [{column_name}] {column_type}")
                    conn.commit()
                    return True
                return False
        except Exception as e:
            print(f"Error adding column to {table_name}: {e}")
            return False

    def insert_lead(self, data_dict):
        """Inserts a lead and creates columns dynamically if they don't exist."""
        # Sanitize data: handle ID conflict and NaN values
        sanitized_data = {}
        for k, v in data_dict.items():
            # Rename 'id' to 'external_id' to avoid conflict with SQLite PRIMARY KEY
            new_key = "external_id" if k.lower() == "id" else k
            # Handle NaN values
            if isinstance(v, float) and pd.isna(v):
                sanitized_data[new_key] = ""
            else:
                sanitized_data[new_key] = str(v) if v is not None else ""

        # Ensure all columns exist in the 'leads' table
        for key in sanitized_data.keys():
            self.add_column("leads", key)

        # Add metadata
        if "import_date" not in sanitized_data:
            sanitized_data["import_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        keys = list(sanitized_data.keys())
        placeholders = ", ".join(["?"] * len(keys))
        columns = ", ".join([f"[{k}]" for k in keys])

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"INSERT INTO leads ({columns}) VALUES ({placeholders})", list(sanitized_data.values()))
            conn.commit()
            return cursor.lastrowid

    def add_interaction(self, lead_id, data_dict):
        """Logs a new interaction for a lead with support for custom fields."""
        if "contact_date" not in data_dict:
            data_dict["contact_date"] = datetime.now().strftime("%Y-%m-%d")
        if "contact_time" not in data_dict:
            data_dict["contact_time"] = datetime.now().strftime("%H:%M:%S")

        data_dict["lead_id"] = lead_id

        # Ensure all columns exist in 'interactions'
        for key in data_dict.keys():
            self.add_column("interactions", key)

        keys = list(data_dict.keys())
        placeholders = ", ".join(["?"] * len(keys))
        columns = ", ".join([f"[{k}]" for k in keys])

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"INSERT INTO interactions ({columns}) VALUES ({placeholders})", list(data_dict.values()))
            conn.commit()
            return cursor.lastrowid

    def delete_record(self, table_name, record_id):
        """Deletes a record from any table by ID."""
        table_name = self._sanitize_sql_name(table_name)
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # If deleting from leads, also delete interactions
            if table_name.lower() == "leads":
                cursor.execute("DELETE FROM interactions WHERE lead_id = ?", (record_id,))

            cursor.execute(f"DELETE FROM [{table_name}] WHERE id = ?", (record_id,))
            conn.commit()
            return True

    def update_record(self, table_name, record_id, col_name, new_value):
        """Updates a specific field of a record in any table."""
        table_name = self._sanitize_sql_name(table_name)
        col_name = self._sanitize_sql_name(col_name)
        with self._get_connection() as conn:
            cursor = conn.cursor()
            query = f"UPDATE [{table_name}] SET [{col_name}] = ? WHERE id = ?"
            cursor.execute(query, (new_value, record_id))
            conn.commit()
            return True

    def fetch_all_leads(self, search_term=None):
        """Returns all leads as a list of dictionaries, optionally filtered by search_term."""
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            if search_term:
                cursor.execute("PRAGMA table_info(leads)")
                columns = [info[1] for info in cursor.fetchall()]
                conditions = " OR ".join([f"[{col}] LIKE ?" for col in columns])
                query = f"SELECT * FROM leads WHERE {conditions} ORDER BY id DESC"
                params = [f"%{search_term}%"] * len(columns)
                cursor.execute(query, params)
            else:
                cursor.execute("SELECT * FROM leads ORDER BY id DESC")

            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def get_table_names(self):
        """Returns a list of all table names in the database."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
            return [row[0] for row in cursor.fetchall()]

    def get_table_data(self, table_name):
        """Returns all data from a specific table."""
        table_name = self._sanitize_sql_name(table_name)
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM [{table_name}]")
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def get_interaction_report(self, start_date=None, end_date=None):
        """Returns interactions joined with lead details, filtered by date."""
        query = """
            SELECT i.*, l.*
            FROM interactions i
            JOIN leads l ON i.lead_id = l.id
        """
        params = []
        if start_date and end_date:
            query += " WHERE i.contact_date BETWEEN ? AND ?"
            params = [start_date, end_date]
        elif start_date:
            query += " WHERE i.contact_date >= ?"
            params = [start_date]
        elif end_date:
            query += " WHERE i.contact_date <= ?"
            params = [end_date]

        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            # Clean up duplicate 'id' and 'lead_id' columns from JOIN if necessary,
            # but usually it's fine for Excel
            return [dict(row) for row in rows]

if __name__ == "__main__":
    # Quick test
    db = DatabaseManager("test_leads.db")
    lead_id = db.insert_lead({"full_name": "Test User", "phone": "123456", "custom_field": "Val"})
    print(f"Inserted lead ID: {lead_id}")
    db.add_interaction(lead_id, {"result": "Called", "notes": "No answer"})
    print("Leads:", db.fetch_all_leads())
    print("Tables:", db.get_table_names())
