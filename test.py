# test_shop.py

import os
import easyLite

def main():
    # Rimuoviamo l'eventuale DB precedente
    db_name = "test_shop.db"
    if os.path.exists(db_name):
        os.remove(db_name)

    # 1) Connettiamo (o creiamo) il database
    db = easyLite.easyLite()
    db.connect(db_name)

    # 2) Creiamo la tabella "users"
    #    id PK AUTOINCREMENT, name, email (NOT NULL UNIQUE), country
    db.newTable("users") \
      .PK() \
      .textCol("name", "NN") \
      .textCol("email", "NN UQ") \
      .textCol("country") \
      .create()

    # 3) Creiamo la tabella "products"
    #    id PK, name, price, stock
    db.newTable("products") \
      .PK() \
      .textCol("name", "NN") \
      .floatCol("price", "NN") \
      .intCol("stock", "NN") \
      .create()

    # 4) Creiamo la tabella "orders"
    #    id PK, user_id (FK->users), product_id (FK->products), quantity
    db.newTable("orders") \
      .PK() \
      .FK("user_id", "users") \
      .FK("product_id", "products", "id") \
      .intCol("quantity", "NN") \
      .create()

    # 5) Aggiungiamo una colonna "age" alla tabella users
    db.addToTable("users") \
      .intCol("age") \
      .add()

    # 6) Inseriamo alcuni utenti (multi inserimento)
    db.recordToTable("users").multiRows([
        ("Mario Rossi",  "mario@example.com", "Italy", 35),
        ("Anna Bianchi", "anna@example.com",  "Italy", 28),
        ("John Doe",     "john@doe.com",      "USA",   42),
    ]).record()

    # 7) Inseriamo un singolo utente con field()
    db.recordToTable("users") \
      .field("name", "Sara Smith") \
      .field("email", "sara@smith.co.uk") \
      .field("country", "UK") \
      .field("age", 30) \
      .record()

    # 8) Inseriamo alcuni prodotti
    db.recordToTable("products").multiRows([
        ("Laptop",   899.99, 10),
        ("Mouse",     19.90, 50),
        ("Keyboard",  49.90, 20),
    ]).record()

    # 9) Visualizziamo i prodotti
    print("\n-- PRODUCTS --")
    prod_res = db.select("products").fetch()
    prod_res.printResult()

    # 10) Creiamo alcuni ordini
    # user_id, product_id, quantity
    # Sfruttiamo la multiRows (occhio all'ordine delle colonne in PRAGMA)
    db.recordToTable("orders").multiRows([
        (1, 1,  2),  # Mario acquista 2 Laptop
        (1, 2,  5),  # Mario acquista 5 Mouse
        (2, 3,  1),  # Anna acquista 1 Keyboard
        (3, 2, 10),  # John acquista 10 Mouse
    ]).record()

    # 11) Stampiamo la tabella orders con join su users e products
    print("\n-- JOIN ORDERS/USERS/PRODUCTS --")
    join_res = db.select("orders") \
                 .fields("orders.id", "users.name", "products.name", "orders.quantity") \
                 .join("users", "orders.user_id = users.id") \
                 .join("products", "orders.product_id = products.id") \
                 .sortBy("orders.id") \
                 .fetch()
    join_res.printResult()

    # 12) Aggiorniamo la 'stock' di un prodotto (es. Laptop) con updateTable
    db.updateTable("products") \
      .where("name = ?", "Laptop") \
      .field("stock", 8) \
      .record()

    # 13) Eseguiamo una query custom: select i prodotti dove stock < 10
    print("\n-- CUSTOM QUERY: PRODUCTS STOCK < 10 --")
    custom_sql = "SELECT * FROM products WHERE stock < ?"
    custom_res = db.executeCustomQuery(custom_sql, (10,))
    custom_res.printResult()

    # 14) Esempio di delete: John Doe abbandona
    db.deleteFromTable("users") \
      .where("name = ?", "John Doe") \
      .execute()

    print("\n-- USERS AFTER DELETE 'John Doe' --")
    users_res = db.select("users").fetch()
    users_res.printResult()

    # 15) Esempio di GROUP BY su orders, per sapere quante volte ogni user_id compare
    print("\n-- GROUP BY user_id on 'orders' --")
    group_res = db.select("orders") \
                  .fields("user_id", "COUNT(*) as total_orders") \
                  .groupBy("user_id") \
                  .fetch()
    group_res.printResult()

    # 16) Visualizziamo schema
    print("\n-- DATABASE SCHEMA --")
    db.getSchema()

    # 17) Pulizia finale: drop tables
    # db.dropTable("orders")
    # db.dropTable("products")
    # db.dropTable("users")

    # 18) Chiusura
    db.close()

if __name__ == "__main__":
    main()
