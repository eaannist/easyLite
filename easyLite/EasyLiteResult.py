# EasyLiteResult.py
import csv
import json
from typing import List, Tuple, Any

# Class to handle query results
class EasyLiteResult:
    # Constructor
    def __init__(self, rows: List[Tuple[Any]], columns: List[str]):
        self._rows = rows
        self._columns = columns

    # Returns all rows
    def rows(self) -> List[Tuple[Any]]:
        return self._rows

    # Returns column names
    def columns(self) -> List[str]:
        return self._columns

    # Returns the CSV representation in memory
    def toCSV(self) -> str:
        try:
            import io
            buffer = io.StringIO()
            writer = csv.writer(buffer)
            writer.writerow(self._columns)
            writer.writerows(self._rows)
            return buffer.getvalue()
        except Exception as e:
            print(f"[ERROR] Failed to generate CSV string: {e}")
            return ""

    # Saves the result as a CSV file
    def saveCSV(self, csv_filename: str):
        try:
            with open(csv_filename, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(self._columns)
                writer.writerows(self._rows)
            print(f"CSV file has been successfully saved to '{csv_filename}'.")
        except Exception as e:
            print(f"[ERROR] Failed to save CSV file '{csv_filename}': {e}")

    # Prints the result in a simple table format
    def printResult(self):
        if not self._columns:
            print("(No columns in result)")
            return
        col_widths = []
        for i, col_name in enumerate(self._columns):
            try:
                max_len_in_col = max((len(str(row[i])) for row in self._rows), default=0)
            except Exception:
                max_len_in_col = 0
            col_widths.append(max(len(col_name), max_len_in_col))
        header_line = " | ".join(col_name.ljust(col_widths[i]) for i, col_name in enumerate(self._columns))
        print(header_line)
        print("-" * len(header_line))
        for row in self._rows:
            row_line = " | ".join(str(row[i]).ljust(col_widths[i]) for i in range(len(self._columns)))
            print(row_line)

    # Returns the result in JSON format
    def toJSON(self) -> str:
        try:
            data = []
            for row in self._rows:
                item = {}
                for col, val in zip(self._columns, row):
                    item[col] = val
                data.append(item)
            return json.dumps(data)
        except Exception as e:
            print(f"[ERROR] Failed to generate JSON: {e}")
            return "[]"
