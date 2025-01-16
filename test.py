import os
from easyLite import eL

def main():
    print('\n[Test] Initialization\n')

    db = eL().connect('test_store.db')

    print('\n[Test] Creating table users\n')

    db.newTable("users") \
      .PK() \
      .textCol("name", "NN") \
      .textCol("email", "NN UQ") \
      .dateCol("birth") \
      .create()

    print('\n[Test] Adding columns to users\n')

    db.addToTable("users") \
      .intCol("age") \
      .floatCol("height") \
      .add()

    print('\n[Test] Checking the schema\n')

    db.getSchema()

    print('\n[Test] Insert into users using .field method\n')

    db.insertIn("users") \
      .field('name','Mario')\
      .field('email','mario@mail.com')\
      .field('age',19)\
      .record()

    print('\n[Test] Insert into users using .row method\n')

    db.insertIn("users")\
      .row('Maria','maria@email.it',db.skip,20)\
      .row('Pierre','pierre@mail.fr', '1999',db.skip,db.skip)\
      .record()

    print('\n[Test] Insert into users using .multiRows method\n')

    db.insertIn("users") \
      .row('Sara','sara@email.com',db.skip,20)\
      .multiRows([
        ("Luigi", "luigi@mail.it", db.null, 40, 1.80),
        ("Carla", "carla@mail.us", "1990", 35, db.skip),
        ("John", "john@mail.us", db.skip, 28, 1.75)
      ]) \
      .record()
    
    print('\n[Test] Selecting users table and showing results\n')

    db.select('users').fetch().show()


    print('\n[Test] Update using .field and db.null\n')

    db.updateIn("users") \
      .where("name = ?", "Paolo") \
      .field('age',26) \
      .field('birth',db.null)\
      .record()
    
    print('\n[Test] Update using .row with db.skip\n')

    db.updateIn("users") \
      .where("age = 20") \
      .row(db.skip,db.skip,'2005') \
      .record()
    
    print('\n[Test] Update using .row with db.skip and db.null\n')

    db.updateIn("users")\
      .row(db.skip,db.skip,db.skip,db.skip,db.null) \
      .record()

    print('\n[Test] Deleting record\n')

    db.deleteIn('users').where("name = ?","Carla").execute()

    print('\n[Test] Showing the result\n')

    db.select('users').fetch().show()

    print('\n[Test] Renaming table\n')

    db.modTable("users").modName("customers")

    print('\n[Test] Removing column from table\n')

    db.modTable("customers").remCol("birth")

    print('\n[Test] Showing the result\n')

    db.select('customers').fetch().show()
     
    print('\n[Test] Creating table countries\n')

    db.newTable("countries") \
      .PK() \
      .textCol("name", "NN") \
      .create()
    db.select('countries').fetch().show()

    print('\n[Test] Adding FK to customers\n')

    db.addToTable('customers').FK('country_id','countries').add()
    
    print('\n[Test] Showing the result\n')

    db.getSchema('customers')
    db.select('customers').fetch().show()

    print('\n[Test] Populating countries table\n')

    db.insertIn("countries")\
      .row("Italy")\
      .row("England")\
      .row("France")\
      .row("USA")\
      .record()
    
    print('\n[Test] Updating country_id in customers table\n')

    db.updateIn('customers').where('email LIKE ?', '%it').field('country_id',1).record()
    db.updateIn('customers').where('email LIKE ?', '%com').field('country_id',2).record()
    db.updateIn('customers').where('email LIKE ?', '%fr').field('country_id',3).record()
    db.updateIn('customers').where('email LIKE ?', '%us').field('country_id',4).record()
    db.select('customers').fetch().show()

    print('\n[Test] Query with join between customers and countries\n')

    res = db.select("customers") \
            .join('country_id','countries')\
            .fields('customers.name','customers.email','customers.age as age','countries.name as country')\
            .sortBy('country','age')\
            .fetch()

    print('\n[Test] Showing the result\n')

    res.show()
    print(f"Total rows: {res.count()}")

    print('\n[Test] Showing result as CSV\n')

    print(res.toCSV())

    print('\n[Test] Showing result as JSON\n')

    print(res.toJSON())

    print("\n[Test] Showing result as API-style JSON ")

    print(res.toApiJSON())

    # print('\n[Test] Exporting result to .csv file\n')

    # res.exportCSV("test.csv")

    # print('\n[Test] Exporting result to .json file\n')

    # res.exportJSON("test.json")

    # print('\n[Test] Dropping countries table\n')

    # db.dropTable("countries")

    # print('\n[Test] Deleting database file\n')

    # db.deleteDatabaseFile()

    print('\n[Test] Closing database connection\n')
    db.close()

if __name__ == "__main__":
    main()
