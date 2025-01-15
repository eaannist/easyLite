# EasyLiteRecord.py
import sqlite3
from typing import List, Dict, Any

class EasyLiteRecord:
    # Constructor
    def __init__(self, connection: sqlite3.Connection, table_name: str, mode: str):
        self.connection = connection
        self.table_name = table_name
        self.mode = mode  # 'insert', 'update', or 'delete'
        self._values_dict: Dict[str, Any] = {}
        self._where_clause: str = ""
        self._where_params: List[Any] = []
        self._table_info: List[Any] = []
        self._multi_rows: List[List[Any]] = []  # for multi insert
        self._load_table_info()

    # Load table info from PRAGMA
    def _load_table_info(self):
        try:
            c = self.connection.cursor()
            c.execute(f"PRAGMA table_info({self.table_name});")
            self._table_info = c.fetchall()
        except sqlite3.Error as e:
            print(f"[ERROR] Failed to load table info for '{self.table_name}': {e}")
            self._table_info = []

    # Single field assignment (INSERT or UPDATE)
    def field(self, column_name: str, value: Any):
        self._values_dict[column_name] = value
        return self

    # Insert a single row by specifying values in the same order as the table columns
    def row(self, *values: Any):
        if not self._table_info:
            print(f"[WARNING] Table info not found for '{self.table_name}'. row(...) cannot map values.")
            return self
        col_index = 0
        for col in self._table_info:
            cid, cname, ctype, notnull, dflt, pk = col
            if col_index < len(values):
                self._values_dict[cname] = values[col_index]
                col_index += 1
            else:
                break
        return self

    # Add multiple rows for insertion
    def multiRows(self, rows: List[List[Any]]):
        if self.mode != "insert":
            print("[ERROR] multiRows(...) can only be used in insert mode.")
            return self
        self._multi_rows.extend(rows)
        return self

    # Set the WHERE clause (only for update/delete)
    def where(self, clause: str, *params):
        self._where_clause = clause
        self._where_params = list(params)
        return self

    # Execute the main action (INSERT, UPDATE, or multi-INSERT)
    def record(self):
        if self.mode == "insert":
            # If we have multiple rows (multiRows), we do a multi-insert
            if self._multi_rows:
                return self._insert_multi()
            else:
                return self._insert_single()
        elif self.mode == "update":
            return self._update_record()
        elif self.mode == "delete":
            print("[ERROR] 'record()' is not valid for delete mode. Use 'execute()' instead.")
        else:
            print("[ERROR] Unknown mode. Must be 'insert', 'update', or 'delete'.")
        return self

    # Execute the delete
    def execute(self):
        if self.mode != "delete":
            print("[ERROR] execute() is for delete mode only.")
            return self
        try:
            sql = f"DELETE FROM {self.table_name}"
            if self._where_clause:
                sql += f" WHERE {self._where_clause}"
            c = self.connection.cursor()
            c.execute(sql, self._where_params)
            self.connection.commit()
            print(f"Successfully deleted records from '{self.table_name}'.")
        except sqlite3.Error as e:
            print(f"[ERROR] Failed to delete records from '{self.table_name}': {e}")
        return self

    # Internal single insert
    def _insert_single(self):
        if not self._values_dict:
            print("[WARNING] No fields set for insert. Nothing will be inserted.")
            return self
        columns = list(self._values_dict.keys())
        placeholders = ", ".join("?" for _ in columns)
        values = [self._values_dict[col] for col in columns]
        col_str = ", ".join(columns)
        sql = f"INSERT INTO {self.table_name} ({col_str}) VALUES ({placeholders})"
        try:
            c = self.connection.cursor()
            c.execute(sql, values)
            self.connection.commit()
            print(f"Successfully inserted a new record into '{self.table_name}'.")
        except sqlite3.Error as e:
            print(f"[ERROR] Failed to insert record into '{self.table_name}': {e}")
        return self

    # Internal multi insert
    def _insert_multi(self):
        if not self._table_info:
            print("[ERROR] Table info not loaded. Multi insert not possible.")
            return self
        if not self._multi_rows:
            print("[WARNING] multiRows is empty. No insertion performed.")
            return self
        # We'll build columns from table_info excluding possible PK autoincrement
        # Alternatively, we keep all columns, but user must pass the correct number
        col_names = [col[1] for col in self._table_info if col is not None]
        # If the first col is PK AUTOINCREMENT, user might skip it
        # We'll do a naive approach: attempt to insert exactly all columns
        placeholders = ", ".join("?" for _ in col_names)
        col_str = ", ".join(col_names)
        sql = f"INSERT INTO {self.table_name} ({col_str}) VALUES ({placeholders})"

        try:
            c = self.connection.cursor()
            # We'll transform each row in self._multi_rows to match col_names length
            for row_vals in self._multi_rows:
                if len(row_vals) != len(col_names):
                    print("[WARNING] The row length does not match the table columns length. Attempting partial insert.")
                    # Attempt partial:
                    row_vals = list(row_vals) + [None]*(len(col_names) - len(row_vals))
                c.execute(sql, row_vals)
            self.connection.commit()
            print(f"Successfully inserted {len(self._multi_rows)} records into '{self.table_name}'.")
        except sqlite3.Error as e:
            print(f"[ERROR] Failed to insert multiple records into '{self.table_name}': {e}")
        return self

    # Internal update
    def _update_record(self):
        if not self._values_dict:
            print("[WARNING] No fields set for update. Nothing will be updated.")
            return self
        set_clause = ", ".join(f"{col} = ?" for col in self._values_dict.keys())
        values = list(self._values_dict.values())
        sql = f"UPDATE {self.table_name} SET {set_clause}"
        if self._where_clause:
            sql += f" WHERE {self._where_clause}"
            values += self._where_params
        else:
            print("[WARNING] No WHERE clause specified. This may update all rows.")
        try:
            c = self.connection.cursor()
            c.execute(sql, values)
            self.connection.commit()
            print(f"Successfully updated records in '{self.table_name}'.")
        except sqlite3.Error as e:
            print(f"[ERROR] Failed to update records in '{self.table_name}': {e}")
        return self
