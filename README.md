# easyLite (v1.4)

**easyLite** is a Python library that simplifies the creation, management, and querying of SQLite databases through a fluent and user-friendly API.

## Key Features

- **Fluent Table Building**: Create and modify tables with readable, chained methods (`newTable`, `addToTable`, `modTable`).
- **CRUD Operations**: Insert, update, and delete records easily.
- **Fluent SELECT Queries**: Build queries with `.where()`, `.groupBy()`, `.join()`, `.sortBy()`, `.limit()`, and more.
- **Result Handling**: Print results, convert them to CSV or JSON, or save them in a file.
- **Schema Inspection**: Use `getSchema()` to view a nicely formatted representation of all tables, columns, and foreign keys.

## Installation

After the library is published on PyPI, you can install it with:

```bash
pip install easyLite
```
Alternatively, you can install it directly from source:

```bash

git clone https://github.com/your-username/easyLite.git
cd easyLite
pip install .
```
## Usage
Below is a detailed guide on how to use easyLite in your Python projects.

1. Basic Setup

```python

from EasyLiteCore import EasyLite

db = EasyLite()
db.connect("my_database.db")  # Creates or opens the SQLite database
```

2. Creating Tables

Use the builder methods to create tables fluently:

```python

db.newTable("users") \
    .PK() \
    .textCol("name", "NN") \
    .textCol("email", "NN UQ") \
    .intCol("age") \
    .floatCol("height") \
    .dateCol("birth") \
    .create()
```
PK() adds a primary key column (id INTEGER PRIMARY KEY AUTOINCREMENT by default).
textCol(), intCol(), floatCol(), dateCol() add typed columns with optional constraints (e.g., "NN", "UQ").
FK(col, ref_table, ref_pk="id") creates a foreign key to another table.

3. Adding Columns to an Existing Table

```python

db.addToTable("users") \
    .textCol("nickname", "UQ") \
    .add()
```

4. Modifying Tables

You can rename the table, modify columns, or remove columns:

```python

# Rename the table
db.modTable("users").modName("persons")

# Modify a column
db.modTable("persons").modCol("nickname").textCol("alias", "NN")

# Remove a column
db.modTable("persons").remCol("birth")
```
5. CRUD Operations

```python

# Insert
db.addRecord("persons", {"name": "Mario", "email": "mario@example.com", "age": 30})

# Update
db.updateRecords("persons", {"age": 31}, "name = ?", ["Mario"])

# Delete
db.deleteRecords("persons", "name = ?", ["Mario"])
```

6. Fluent SELECT Queries

```python

res = db.select("persons") \
        .fields("id", "name", "email") \
        .where("age > ?", 25) \
        .sortBy("age", ascending=False) \
        .limit(10) \
        .fetch()

# Print results in a nice table
res.printResult()

# Convert the result to CSV in memory
csv_data = res.toCSV()

# Save the result to a file
res.saveCSV("persons.csv")

# Convert to JSON
json_data = res.toJSON()
```
7. Joining Tables

```python

join_res = db.select("persons") \
    .fields("persons.id", "persons.name", "ranks.rank_name") \
    .join("user_ranks", "persons.id = user_ranks.user_id") \
    .join("ranks", "user_ranks.rank_id = ranks.rank_id") \
    .fetch()

join_res.printResult()
```

8. Inspecting the Schema

```python

db.getSchema()
This will print out all user-defined tables, their columns, and foreign keys in a readable format.
```

9. Dropping Tables

```python

db.dropTable("persons")
```
10. Closing the Connection
```python

db.close()
```