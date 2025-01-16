# EasyLiteRecord.py
import sqlite3
from typing import Any, List, Dict

class EasyLiteRecord:
    def __init__(self, core, table_name: str, mode: str):
        self.core = core
        self.connection = core.connection
        self.table_name = table_name
        self.mode = mode
        self._values_dict: Dict[str, Any] = {}
        self._where_clause: str = ""
        self._where_params: List[Any] = []
        self._table_info: List[Any] = []
        self._multi_rows: List[List[Any]] = []
        self._load_table_info()

    def _load_table_info(self):
        try:
            c = self.connection.cursor()
            c.execute(f"PRAGMA table_info({self.table_name});")
            self._table_info = c.fetchall()
        except sqlite3.Error as e:
            print(f"[ERROR] Failed to load table info for '{self.table_name}': {e}")
            self._table_info = []

    def row(self, *values: Any):
        if self.mode not in ("insert", "update"):
            print(f"[ERROR] .row(...) can only be used in 'insert' or 'update' mode (current: {self.mode}).")
            return self

        # insert mode -> accumulate in _multi_rows
        if self.mode == "insert":
            self._multi_rows.append(values)
            return self

        # update mode -> map row values into _values_dict for non-PK columns
        if self.mode == "update":
            non_pk_cols = [col for col in self._table_info if col[5] == 0]
            col_names = [c[1] for c in non_pk_cols]
            usable_count = min(len(values), len(col_names))

            for i in range(usable_count):
                val = values[i]
                col_name = col_names[i]
                if val is self.core.skip:
                    continue
                elif val is self.core.null:
                    self._values_dict[col_name] = None
                else:
                    self._values_dict[col_name] = val

            return self

    def multiRows(self, rows: List[List[Any]]):
        if self.mode != "insert":
            print("[ERROR] multiRows(...) can only be used in 'insert' mode.")
            return self
        self._multi_rows.extend(rows)
        return self

    def field(self, column_name: str, value: Any):
        # if user provides db.skip, do nothing
        if value is self.core.skip:
            return self

        # if user provides db.null, store None so SQLite can handle it
        if value is self.core.null:
            self._values_dict[column_name] = None
        else:
            self._values_dict[column_name] = value

        return self

    def where(self, clause: str, *params):
        self._where_clause = clause
        self._where_params = list(params)
        return self

    def record(self):
        if self.mode == "insert":
            if self._multi_rows:
                return self._insert_multi()
            else:
                return self._insert_single()
        elif self.mode == "update":
            return self._update_record()
        elif self.mode == "delete":
            print("[ERROR] 'record()' not valid for delete mode. Use 'execute()'.")
        else:
            print("[ERROR] Unknown mode.")
        return self

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
            print(f"[SUCCESS] Records deleted from '{self.table_name}'.")
        except sqlite3.Error as e:
            print(f"[ERROR] {e}")
        return self

    def _insert_single(self):
        if not self._values_dict:
            print("[WARNING] No fields set for insert, and no rows queued. Nothing inserted.")
            return self

        cols = list(self._values_dict.keys())
        placeholders = ", ".join("?" for _ in cols)
        vals = [self._values_dict[c] for c in cols]

        sql = f"INSERT INTO {self.table_name} ({', '.join(cols)}) VALUES ({placeholders})"
        try:
            c = self.connection.cursor()
            c.execute(sql, vals)
            self.connection.commit()
            print(f"[SUCCESS] Inserted a new record into '{self.table_name}'.")
        except sqlite3.Error as e:
            print(f"[ERROR] {e}")
        return self

    def _insert_multi(self):
        if not self._table_info:
            print("[ERROR] Table info not loaded. Multi insert impossible.")
            return self

        non_pk = [col for col in self._table_info if col[5] == 0]
        col_names = [c[1] for c in non_pk]
        placeholders = ", ".join("?" for _ in col_names)
        sql = f"INSERT INTO {self.table_name} ({', '.join(col_names)}) VALUES ({placeholders})"

        c = self.connection.cursor()
        inserted_count = 0

        try:
            for row_vals in self._multi_rows:
                final_vals = []
                for i in range(len(col_names)):
                    if i < len(row_vals):
                        v = row_vals[i]
                        if v is self.core.skip:
                            final_vals.append(None)
                        elif v is self.core.null:
                            final_vals.append(None)
                        else:
                            final_vals.append(v)
                    else:
                        final_vals.append(None)
                c.execute(sql, final_vals)
                inserted_count += 1
            self.connection.commit()
            print(f"[SUCCESS] Inserted {inserted_count} records into '{self.table_name}'.")
        except sqlite3.Error as e:
            print(f"[ERROR] {e}")
        return self

    def _update_record(self):
        if not self._values_dict:
            print("[WARNING] No fields set for update. Nothing will be updated.")
            return self

        set_clause = ", ".join(f"{col} = ?" for col in self._values_dict.keys())
        vals = list(self._values_dict.values())

        sql = f"UPDATE {self.table_name} SET {set_clause}"

        if self._where_clause:
            sql += f" WHERE {self._where_clause}"
            vals += self._where_params
        else:
            print("[WARNING] No WHERE clause specified. Updating ALL rows.")

        try:
            c = self.connection.cursor()
            c.execute(sql, vals)
            self.connection.commit()
            print(f"[SUCCESS] Updated records in '{self.table_name}'.")
        except sqlite3.Error as e:
            print(f"[ERROR] {e}")

        return self
