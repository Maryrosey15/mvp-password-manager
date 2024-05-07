import sqlite3

conn = sqlite3.connect('database.db')
print("Connected to database successfully")

conn.execute('CREATE TABLE accounts (email TEXT, username TEXT, password TEXT, website TEXT, image BLOB)')
print("Created table successfully")

conn.close()


conn = sqlite3.connect('database.db')
print("Connected to database successfully")

conn.execute('CREATE TABLE users (email TEXT, username TEXT, master_password TEXT)')
print("Created table successfully")

conn.close()
