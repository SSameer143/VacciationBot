import sqlite3


class VaccinationDB:

    def __init__(self, dbname="vaccination.sqlite"):
        self.dbname = dbname
        self.conn = sqlite3.connect(dbname)

    def setup(self):
        create_table = "CREATE TABLE IF NOT EXISTS items (owner_id integer primary key, name text default  null, location text default null,service text default null,date text default null,slot text default null)"
        self.conn.execute(create_table)
        self.conn.commit()

    def add_item(self, owner_id, name=None, location=None,service=None, date=None, slot=None):
        query = "INSERT INTO items (owner_id, name, location, service, date, slot) VALUES (?, ?,?,?,?,?)"
        args = (owner_id, name, location,service, date, slot)
        self.conn.execute(query, args)
        self.conn.commit()

    def update_item(self, owner_id, column,data):
        query = "UPDATE items SET {} = ? WHERE owner_id = ?".format(column)
        args =(data,owner_id)
        self.conn.execute(query,args)
        self.conn.commit()

    def check_slot(self,date):
        query = "SELECT slot FROM items WHERE date = (?)"
        args = (date,)
        return self.conn.execute(query, args)

    def delete_item(self, owner):
        query = "DELETE FROM items WHERE owner_id = (?)"
        args = (owner,)
        self.conn.execute(query, args)
        self.conn.commit()

    def get_items(self, owner):
        stmt = "SELECT * FROM items WHERE owner_id = (?)"
        args = (owner, )
        return self.conn.execute(stmt, args)
