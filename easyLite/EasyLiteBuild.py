# EasyLiteBuild.py
import sqlite3

# Class for building or modifying tables
class EasyLiteBuild:
    # Constructor
    def __init__(self, connection: sqlite3.Connection, table_name: str, mode: str):
        self.connection = connection
        self.table_name = table_name
        self.mode = mode
        self._cols_def = []
        self._fks_def = []
        self._pk_defined = False
        self._col_to_modify = None

    # Create a PK column
    def PK(self, name="id", autoincrement=True):
        if self._pk_defined:
            return self
        pk = f"{name} INTEGER PRIMARY KEY"
        if autoincrement:
            pk += " AUTOINCREMENT"
        self._cols_def.append(pk)
        self._pk_defined = True
        return self

    # Create a TEXT column
    def textCol(self, name: str, constraints: str = ""):
        if self.mode == "modtable" and self._col_to_modify:
            cd = self._buildColumnDef(name, "TEXT", constraints)
            self._modifyColumn(self._col_to_modify, cd)
            self._col_to_modify = None
            return self
        if self.mode in ["newtable", "addcolumns"]:
            cd = self._buildColumnDef(name, "TEXT", constraints)
            self._cols_def.append(cd)
        return self

    # Create an INTEGER column
    def intCol(self, name: str, constraints: str = ""):
        if self.mode == "modtable" and self._col_to_modify:
            cd = self._buildColumnDef(name, "INTEGER", constraints)
            self._modifyColumn(self._col_to_modify, cd)
            self._col_to_modify = None
            return self
        if self.mode in ["newtable", "addcolumns"]:
            cd = self._buildColumnDef(name, "INTEGER", constraints)
            self._cols_def.append(cd)
        return self

    # Create a REAL column
    def floatCol(self, name: str, constraints: str = ""):
        if self.mode == "modtable" and self._col_to_modify:
            cd = self._buildColumnDef(name, "REAL", constraints)
            self._modifyColumn(self._col_to_modify, cd)
            self._col_to_modify = None
            return self
        if self.mode in ["newtable", "addcolumns"]:
            cd = self._buildColumnDef(name, "REAL", constraints)
            self._cols_def.append(cd)
        return self

    # Create a DATE column
    def dateCol(self, name: str, constraints: str = ""):
        if self.mode == "modtable" and self._col_to_modify:
            cd = self._buildColumnDef(name, "DATE", constraints)
            self._modifyColumn(self._col_to_modify, cd)
            self._col_to_modify = None
            return self
        if self.mode in ["newtable", "addcolumns"]:
            cd = self._buildColumnDef(name, "DATE", constraints)
            self._cols_def.append(cd)
        return self

    # Create a foreign key
    def FK(self, column_name: str, ref_table: str, ref_pk: str = "id"):
        if self.mode == "modtable":
            if self._col_to_modify:
                self._col_to_modify = None
            # Not supported to add an FK in modtable
            raise NotImplementedError("Cannot add a foreign key in 'modtable' mode.")
        col_def = f"{column_name} INTEGER"
        self._cols_def.append(col_def)
        fk_def = f"FOREIGN KEY ({column_name}) REFERENCES {ref_table}({ref_pk})"
        self._fks_def.append(fk_def)
        return self

    # Build the table
    def create(self):
        if self.mode != "newtable":
            raise ValueError("create() can only be used in 'newtable' mode.")
        all_defs = self._cols_def + self._fks_def
        defs_str = ", ".join(all_defs)
        sql = f"CREATE TABLE IF NOT EXISTS {self.table_name} ( {defs_str} );"
        try:
            c = self.connection.cursor()
            c.execute(sql)
            self.connection.commit()
            print(f"[SUCCESS] Table '{self.table_name}' created or already exists.")
        except sqlite3.Error as e:
            print(f"[ERROR] Failed to create table '{self.table_name}': {e}")
        return self

    # Switch to addcolumns mode
    def add(self):
        if self.mode != "addcolumns":
            raise ValueError("add() can only be used in 'addcolumns' mode.")
        c = self.connection.cursor()
        for col_def in self._cols_def:
            try:
                sql = f"ALTER TABLE {self.table_name} ADD COLUMN {col_def};"
                c.execute(sql)
                self.connection.commit()
                print(f"[SUCCESS] Column '{col_def}' has been added to '{self.table_name}'.")
            except sqlite3.Error as e:
                print(f"[ERROR] Failed to add column '{col_def}' to '{self.table_name}': {e}")
        if len(self._fks_def) > 0:
            print("[WARNING] Adding a foreign key after table creation hcan corrupt references to the table in any existing triggers, views, and foreign key constraints.")
            self._addFK()
        return self

    # Switch to modtable mode
    def modTable(self, table_name: str):
        self.table_name = table_name
        self.mode = "modtable"
        return self

    # Rename the table
    def modName(self, new_name: str):
        if self.mode != "modtable":
            raise ValueError("modName() can only be used in 'modtable' mode.")
        try:
            c = self.connection.cursor()
            sql = f"ALTER TABLE {self.table_name} RENAME TO {new_name};"
            c.execute(sql)
            self.connection.commit()
            print(f"[SUCCESS] Table '{self.table_name}' was renamed to '{new_name}'.")
            self.table_name = new_name
        except sqlite3.Error as e:
            print(f"[ERROR] Failed to rename table '{self.table_name}' to '{new_name}': {e}")
        return self

    # Start column modify
    def modCol(self, old_col_name: str):
        if self.mode != "modtable":
            raise ValueError("modCol() can only be used in 'modtable' mode.")
        self._col_to_modify = old_col_name
        return self

    # Remove a column
    def remCol(self, column_name: str):
        if self.mode != "modtable":
            raise ValueError("remCol() can only be used in 'modtable' mode.")
        try:
            info = self._getTableInfo()
            new_schema = []
            for col in info:
                cid, cname, ctype, notnull, dflt, pk = col
                if cname == column_name:
                    continue
                base = f"{cname} {ctype}"
                if notnull:
                    base += " NOT NULL"
                if dflt is not None:
                    base += f" DEFAULT {dflt}"
                if pk:
                    base += " PRIMARY KEY"
                new_schema.append(base)
            temp = f"{self.table_name}_temp_remove"
            c = self.connection.cursor()
            create_temp = f"CREATE TABLE {temp} ( {', '.join(new_schema)} );"
            c.execute(create_temp)
            orig_cols = [x[1] for x in info if x[1] != column_name]
            new_cols = [x.split()[0] for x in new_schema]
            copy_sql = f"INSERT INTO {temp} ({', '.join(new_cols)}) SELECT {', '.join(orig_cols)} FROM {self.table_name};"
            c.execute(copy_sql)
            drop_sql = f"DROP TABLE {self.table_name};"
            c.execute(drop_sql)
            rename_sql = f"ALTER TABLE {temp} RENAME TO {self.table_name};"
            c.execute(rename_sql)
            self.connection.commit()
            print(f"[SUCCESS] Column '{column_name}' has been removed from '{self.table_name}'.")
        except sqlite3.Error as e:
            print(f"[ERROR] Failed to remove column '{column_name}' from '{self.table_name}': {e}")
        return self

    # Internal method to modify a column
    def _modifyColumn(self, old_col_name: str, new_def: str):
        try:
            info = self._getTableInfo()
            new_schema = []
            new_col_name = new_def.split()[0]
            for col in info:
                cid, cname, ctype, notnull, dflt, pk = col
                if cname == old_col_name:
                    new_schema.append(new_def)
                else:
                    base = f"{cname} {ctype}"
                    if notnull:
                        base += " NOT NULL"
                    if dflt is not None:
                        base += f" DEFAULT {dflt}"
                    if pk:
                        base += " PRIMARY KEY"
                    new_schema.append(base)
            temp = f"{self.table_name}_temp_alter"
            c = self.connection.cursor()
            create_temp = f"CREATE TABLE {temp} ( {', '.join(new_schema)} );"
            c.execute(create_temp)
            orig_cols = [x[1] for x in info]
            new_cols = [x.split()[0] for x in new_schema]
            old_list = []
            new_list = []
            for oc in orig_cols:
                if oc == old_col_name:
                    if new_col_name in new_cols:
                        old_list.append(oc)
                        new_list.append(new_col_name)
                else:
                    if oc in new_cols:
                        old_list.append(oc)
                        new_list.append(oc)
            copy_sql = f"INSERT INTO {temp} ({', '.join(new_list)}) SELECT {', '.join(old_list)} FROM {self.table_name};"
            c.execute(copy_sql)
            drop_sql = f"DROP TABLE {self.table_name};"
            c.execute(drop_sql)
            rename_sql = f"ALTER TABLE {temp} RENAME TO {self.table_name};"
            c.execute(rename_sql)
            self.connection.commit()
            print(f"[SUCCESS] Column '{old_col_name}' was modified to '{new_def}' in '{self.table_name}'.")
        except sqlite3.Error as e:
            print(f"[ERROR] Failed to modify column '{old_col_name}' in '{self.table_name}': {e}")

    # Internal method to add FK(s) to anexisting table
    def _addFK(self):
        # Connect to the SQLite database
        cursor = self.connection.cursor()
        table_name = self.table_name
        new_fk_definitions = self._fks_def
        try:
            # Get existing table schema
            cursor.execute(f"PRAGMA table_info({table_name})")
            table_info = cursor.fetchall()
            # Extract primary key and column definitions
            existing_columns_definitions = []
            existing_pk_columns = []
            for column in table_info:
                col_name = column[1]
                col_type = column[2]
                not_null = "NOT NULL" if column[3] else ""
                default_val = f"DEFAULT {column[4]}" if column[4] is not None else ""
                pk = column[5]  # Primary key flag
                # Build column definition
                column_definition = f"{col_name} {col_type} {not_null} {default_val}".strip()
                existing_columns_definitions.append(column_definition)
                # Track primary key columns
                if pk:
                    existing_pk_columns.append(col_name)
            # Build the primary key definition
            if existing_pk_columns:
                existing_pk_definition = f"PRIMARY KEY ({', '.join(existing_pk_columns)})"
            else:
                existing_pk_definition = ""
            # Combine all column definitions
            existing_columns_definitions_sql = ",\n    ".join(existing_columns_definitions)
            # Combine existing and new foreign key definitions
            new_fks_definitions_sql = ",\n    ".join(new_fk_definitions)
            # Assemble the CREATE TABLE statement
            create_table_sql = f"""
            CREATE TABLE {table_name}_new (
                {existing_columns_definitions_sql},
                {existing_pk_definition},
                {new_fks_definitions_sql}
            );
            """
            # Remove empty lines from SQL
            create_table_sql = "\n".join([line.strip() for line in create_table_sql.splitlines() if line.strip()])
            # Begin transaction and execute the schema modification
            cursor.execute("PRAGMA foreign_keys = OFF;")
            cursor.execute("BEGIN TRANSACTION;")
            cursor.execute(create_table_sql)
            cursor.execute(f"INSERT INTO {table_name}_new SELECT * FROM {table_name};")
            cursor.execute(f"DROP TABLE {table_name};")
            cursor.execute(f"ALTER TABLE {table_name}_new RENAME TO {table_name};")
            cursor.execute("COMMIT;")
            cursor.execute("PRAGMA foreign_keys = ON;")
            print(f"[SUCCESS] FK(s) successfully added to table '{table_name}'.")

        except sqlite3.Error as e:
            # Roll back in case of an error
            self.connection.rollback()
            print(f"[ERROR] Failed to add FK(s) to '{self.table_name}': {e}")


    # Internal method to get table info
    def _getTableInfo(self):
        c = self.connection.cursor()
        c.execute(f"PRAGMA table_info({self.table_name});")
        return c.fetchall()

    # Internal method to build column definition
    def _buildColumnDef(self, name: str, ctype: str, constraints: str):
        parts = []
        upper_con = constraints.upper()
        if "NN" in upper_con or "NOT NULL" in upper_con:
            parts.append("NOT NULL")
        if "UQ" in upper_con or "UNIQUE" in upper_con:
            parts.append("UNIQUE")
        joined = " ".join(parts)
        return f"{name} {ctype} {joined}".strip()
