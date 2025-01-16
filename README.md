# easyLite
- Version **1.7**

**easyLite** is a Python library designed to simplify interactions with SQLite databases. With its fluent and intuitive interface, easyLite makes it effortless to interacting with SQLite databases.

## Features

- **Fluent API**: Chainable methods for database operations.
- **Schema Management**: Easily create and modify tables with constraints and foreign keys.
- **Data Manipulation**: Insert, update, delete, and query records with minimal boilerplate.
- **Advanced Querying**: Support for joins, sorting, and conditional selections.
- **Data Export**: Export query results to CSV or JSON.
- **Schema Inspection**: Retrieve and display the database schema.

---

## Installation

To install easyLite, use:
```bash
pip install easyLite
```

---

## Usage Guide

Below is a step-by-step guide to using easyLite based on the provided test script (which is recommended to try).

### 1. Initialization
```python
from easyLite import eL

db = eL().connect('test_store.db')
```
Establish a connection to the SQLite database.

### 2. Creating a Table
```python
db.newTable("users") \
  .PK() \
  .textCol("name", "NN") \
  .textCol("email", "NN UQ") \
  .dateCol("birth") \
  .create()
```
Create a table named `users` with a primary key, non-nullable text columns, and a date column.

### 3. Adding Columns
```python
db.addToTable("users") \
  .intCol("age") \
  .floatCol("height") \
  .add()
```
Add integer and float columns to the `users` table.

### 4. Inserting Data
#### Using the `.field` Method
```python
db.insertIn("users") \
  .field('name', 'Mario') \
  .field('email', 'mario@mail.com') \
  .field('age', 19) \
  .record()
```
#### Using the `.row` Method
```python
db.insertIn("users") \
  .row('Maria', 'maria@email.it', db.skip, 20) \
  .record()
```
#### Using the `.multiRows` Method
```python
db.insertIn("users") \
  .multiRows([
    ("Luigi", "luigi@mail.it", db.null, 40, 1.80),
    ("Carla", "carla@mail.us", "1990", 35, db.skip),
    ("John", "john@mail.us", db.skip, 28, 1.75)
  ]) \
  .record()
```

### 5. Querying Data
```python
db.select('users').fetch().show()
```
Fetch and display all rows from the `users` table.

### 6. Updating Records
#### Using `.field`
```python
db.updateIn("users") \
  .where("name = ?", "Paolo") \
  .field('age', 26) \
  .field('birth', db.null) \
  .record()
```
#### Using `.row`
```python
db.updateIn("users") \
  .where("age = 20") \
  .row(db.skip, db.skip, '2005') \
  .record()
```

### 7. Managing Tables
#### Renaming a Table
```python
db.modTable("users").modName("customers")
```
#### Removing a Column
```python
db.modTable("customers").remCol("birth")
```

### 8. Working with Foreign Keys
#### Creating a Related Table
```python
db.newTable("countries") \
  .PK() \
  .textCol("name", "NN") \
  .create()
```
#### Adding a Foreign Key
```python
db.addToTable('customers').FK('country_id', 'countries').add()
```
#### Updating Foreign Key Relationships
```python
db.updateIn('customers').where('email LIKE ?', '%it').field('country_id', 1).record()
```

### 9. Exporting Data
#### Export to CSV
```python
res.exportCSV("output.csv")
```
#### Export to JSON
```python
res.exportJSON("output.json")
```
### 10. Deleting and Closing
#### Drop table
```python
db.dropTable("customers")
```
#### Delete .db file and close connection
```python
db.deleteDatabaseFileAndClose(self)
```
#### Close connection
```python
db.close("output.csv")
```
---

## Development Status

**easyLite** is a work-in-progress personal project. Suggestions, feature requests, and constructive feedback are highly welcome. Feel free to open an issue or submit a pull request.

---

## License
This project is licensed under the MIT License.

