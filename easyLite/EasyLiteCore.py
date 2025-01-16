# EasyLiteCore.py
import os
import sqlite3
from .EasyLiteBuild import EasyLiteBuild
from .EasyLiteQuery import EasyLiteQuery
from .EasyLiteRecord import EasyLiteRecord
from .EasyLiteResult import EasyLiteResult


# Main class for database operations
class EasyLiteCore:
    # Constructor
    def __init__(self):
        self.connection = None
        self.cursor = None
        self.db_path = None
        self.skip=object()
        self.null=object()

    # Connect to or create a SQLite database
    def connect(self, db_path: str):
        try:
            db_exists = os.path.exists(db_path)
            self.connection = sqlite3.connect(db_path)
            self.cursor = self.connection.cursor()
            self.db_path = db_path
            if db_exists:
                print(f"[SUCCESS] Successfully connected to existing database: '{db_path}'.")
            else:
                print(f"[SUCCESS] Database file did not exist. A new database has been created: '{db_path}'.")
        except sqlite3.Error as e:
            print(f"[ERROR] Could not connect to the database: {e}")
        return self

    # Returns a builder for creating a new table
    def newTable(self, table_name: str) -> EasyLiteBuild:
        return EasyLiteBuild(self.connection, table_name, mode="newtable")

    # Returns a builder for adding columns to an existing table
    def addToTable(self, table_name: str) -> EasyLiteBuild:
        return EasyLiteBuild(self.connection, table_name, mode="addcolumns")

    # Returns a builder for modifying an existing table
    def modTable(self, table_name: str) -> EasyLiteBuild:
        return EasyLiteBuild(self.connection, table_name, mode="modtable")

    # Insert resord(s)
    def insertIn(self, table_name: str):
        return EasyLiteRecord(self, table_name, mode="insert")

    # Update resord(s)
    def updateIn(self, table_name: str):
        return EasyLiteRecord(self, table_name, mode="update")

    # Delete resord(s)
    def deleteIn(self, table_name: str):
        return EasyLiteRecord(self, table_name, mode="delete")

    # Builds a SELECT query
    def select(self, table_name: str) -> EasyLiteQuery:
        return EasyLiteQuery(self.connection, table_name)

    # Execute a custom SQL query
    def executeCustomQuery(self, sql: str, params: tuple = ()) -> EasyLiteResult:
        try:
            c = self.connection.cursor()
            c.execute(sql, params)
            rows = []
            col_names = []
            try:
                rows = c.fetchall()
                col_names = [desc[0] for desc in c.description]
            except sqlite3.ProgrammingError:
                pass
            self.connection.commit()
            return EasyLiteResult(rows, col_names)
        except sqlite3.Error as e:
            print(f"[ERROR] Custom query failed: {e}")
            return EasyLiteResult([], [])

    # Drop an existing table
    def dropTable(self, table_name: str):
        q = f"DROP TABLE IF EXISTS {table_name};"
        try:
            self.cursor.execute(q)
            self.connection.commit()
            print(f"[SUCCESS] Successfully dropped table '{table_name}' (if it existed).")
        except sqlite3.Error as e:
            print(f"[ERROR] Failed to drop table '{table_name}': {e}")

    # Print a formatted database schema
    def getSchema(self, table_name=None):
        try:
            c = self.connection.cursor()
            if table_name:
                tables = [(table_name,)]
            else:
                c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name;")
                tables = c.fetchall()
            if not tables:
                print("[ERROR] No user-defined tables found in the database.")
                return
            print("=== DATABASE SCHEMA ===\n")
            for i, (tname,) in enumerate(tables, start=1):
                print(f"{i}) Table: {tname}")
                try:
                    c.execute(f"PRAGMA table_info({tname});")
                    cols = c.fetchall()
                    print("   Columns:")
                    for col in cols:
                        cid, name, ctype, notnull, dflt, pk = col
                        nn = " NOT NULL" if notnull else ""
                        pkstr = " [PK]" if pk else ""
                        df = f" DEFAULT {dflt}" if dflt is not None else ""
                        print(f"     - {name} {ctype}{nn}{df}{pkstr}")

                    c.execute(f"PRAGMA foreign_key_list({tname});")
                    fks = c.fetchall()
                    if fks:
                        print("   Foreign Keys:")
                        for fk in fks:
                            _, _, rtab, col_local, col_remote, on_up, on_del, _ = fk
                            print(f"     - {col_local} -> {rtab}({col_remote}) (ON UPDATE {on_up}, ON DELETE {on_del})")
                    else:
                        print("   Foreign Keys: none")
                except sqlite3.Error as e:
                    print(f"[ERROR] Could not retrieve schema info for table '{tname}': {e}")
                print("")
        except sqlite3.Error as e:
            print(f"[ERROR] Could not retrieve database schema: {e}")

    # Delete database file
    def deleteDatabaseFile(self):
        self.close()
        os.remove(self.db_path)

    # Close the database connection
    def close(self):
        if self.connection:
            try:
                self.connection.close()
                self.connection = None
                print("[SUCCESS] Database connection has been closed.")
            except sqlite3.Error as e:
                print(f"[ERROR] Failed to close the database connection: {e}")

