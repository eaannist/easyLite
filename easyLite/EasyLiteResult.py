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

    # Returns the total number of rows
    def count(self) -> int:
        return len(self._rows)

    # Returns a list of dicts, each dict representing a row
    def toDict(self) -> List[dict]:
        data = []
        for row in self._rows:
            item = {}
            for col, val in zip(self._columns, row):
                item[col] = val
            data.append(item)
        return data

    # Returns the CSV content as a string
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

    # Exports the result to a CSV file
    def exportCSV(self, csv_filename: str):
        try:
            with open(csv_filename, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(self._columns)
                writer.writerows(self._rows)
            print(f"[SUCCESS] CSV file has been successfully exported to '{csv_filename}'.")
        except Exception as e:
            print(f"[ERROR] Failed to export CSV file '{csv_filename}': {e}")

    # Shorter, nicer name for printing results
    def show(self):
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

    # Returns the result in a standard JSON array
    def toJSON(self) -> str:
        try:
            return json.dumps(self.toDict())
        except Exception as e:
            print(f"[ERROR] Failed to generate JSON: {e}")
            return "[]"

    # Exports the result as a JSON file with minimal wrapping
    def exportJSON(self, json_filename: str):
        try:
            data_str = self.toJSON()
            with open(json_filename, "w", encoding="utf-8") as f:
                f.write(data_str)
            print(f"[SUCCESS] JSON file has been successfully exported to '{json_filename}'.")
        except Exception as e:
            print(f"[ERROR] Failed to export JSON file '{json_filename}': {e}")

    # Returns the result in an "API style" JSON, e.g. with status, count, data
    def toApiJSON(self) -> str:
        try:
            api_data = {
                "status": "success",
                "count": self.count(),
                "data": self.toDict()
            }
            return json.dumps(api_data)
        except Exception as e:
            print(f"[ERROR] Failed to generate API JSON: {e}")
            return '{"status":"error","count":0,"data":[]}'
