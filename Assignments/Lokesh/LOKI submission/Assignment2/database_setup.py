import sqlite3

conn = sqlite3.connect('user_base.db')
print("Opened database successfully")

conn.execute('CREATE TABLE users (firstname TEXT, lastname TEXT, email TEXT, phone TEXT, password TEXT, dob TEXT)')
print("Table created successfully")
conn.close()