# EasyLiteQuery.py
import sqlite3
from typing import List, Tuple, Any
from .EasyLiteResult import EasyLiteResult

# Class for building SELECT queries
class EasyLiteQuery:
    # Constructor
    def __init__(self, connection: sqlite3.Connection, table_name: str):
        self.connection = connection
        self.table_name = table_name
        self._fields = ["*"]
        self._where_clauses = []
        self._group_by_columns = []
        self._order_clause = None
        self._limit_count = None
        self._params = []
        self._joins = []

    # Select specific fields
    def fields(self, *fields: str):
        if fields:
            self._fields = list(fields)
        return self

    # Add a WHERE clause
    def where(self, clause: str, *params):
        self._where_clauses.append(clause)
        self._params.extend(params)
        return self

    # Fluent join by referencing a local FK and a remote PK
    def join(self, local_field: str, target_table: str, target_pk: str = "id", join_type: str = "INNER"):
        condition = f"{self.table_name}.{local_field} = {target_table}.{target_pk}"
        self._joins.append((target_table, condition, join_type.upper()))
        return self

    # Custom join for arbitrary ON conditions
    def customJoin(self, other_table: str, on_condition: str, join_type: str = "INNER"):
        self._joins.append((other_table, on_condition, join_type.upper()))
        return self

    # Add a GROUP BY clause
    def groupBy(self, *columns: str):
        for c in columns:
            self._group_by_columns.append(c)
        return self

    # Add an ORDER BY clause
    def sortBy(self, column_name: str, ascending: bool = True):
        direction = "ASC" if ascending else "DESC"
        self._order_clause = (column_name, direction)
        return self

    # Add a LIMIT
    def limit(self, count: int):
        self._limit_count = count
        return self

    # Execute and return results
    def fetch(self) -> EasyLiteResult:
        sql, params = self._build_sql()
        try:
            c = self.connection.cursor()
            c.execute(sql, params)
            rows = c.fetchall()
            cols = [d[0] for d in c.description] if c.description else []
            print('[SUCCESS] Query executed, EasyLiteResult object returned.')
            return EasyLiteResult(rows, cols)
        except sqlite3.Error as e:
            print(f"[ERROR] Failed to execute SELECT query on '{self.table_name}': {e}")
            return EasyLiteResult([], [])

    # Build the final SQL query
    def _build_sql(self) -> Tuple[str, list]:
        fstr = ", ".join(self._fields)
        sql = f"SELECT {fstr} FROM {self.table_name}"

        # Build joins
        for (tbl, cond, jtype) in self._joins:
            sql += f" {jtype} JOIN {tbl} ON {cond}"

        # WHERE
        if self._where_clauses:
            w = " AND ".join(self._where_clauses)
            sql += f" WHERE {w}"

        # GROUP BY
        if self._group_by_columns:
            g = ", ".join(self._group_by_columns)
            sql += f" GROUP BY {g}"

        # ORDER BY
        if self._order_clause:
            col, direct = self._order_clause
            sql += f" ORDER BY {col} {direct}"

        # LIMIT
        if self._limit_count is not None:
            sql += f" LIMIT {self._limit_count}"

        return sql, self._params
