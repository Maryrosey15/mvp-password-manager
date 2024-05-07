from flask import Flask
from flask import render_template
from flask import request
import sqlite3

app = Flask(__name__, template_folder='src')

# Database
conn = sqlite3.connect('database.db')
print("Connected to database successfully")

conn.execute('CREATE TABLE IF NOT EXISTS accounts (email TEXT, username TEXT, password TEXT, website TEXT, image BLOB)')
print("Created table successfully")

conn.close()


conn = sqlite3.connect('database.db')
print("Connected to database successfully")

conn.execute('CREATE TABLE IF NOT EXISTS users (email TEXT, username TEXT, master_password TEXT)')
print("Created table successfully")

conn.close()



# Login Page
@app.route("/", methods=['GET', 'POST'])
def login():
    # if request.method == 'POST':
    #     email = request.form['email']
    #     master_password = request.form['master_password']

    #     with sqlite3.connect('database.db') as users:
    #         cur = users.cursor()
    #         cur.execute('SELECT FROM users WHERE email = ?', (email,)
    #                     ).fetchone()
            
    #         if

    return render_template("login.html")


# Register Page
@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        master_password = request.form['master_password']

        with sqlite3.connect("database.db") as users:
            cur = users.cursor()
            cur.execute("INSERT INTO users (email,username,master_password) VALUES (?,?,?)",
                        (email, username, master_password))
            users.commit()
        return render_template("login.html")
    else:
        return render_template("registration.html")


@app.route("/forgot")
def forgot():
    return render_template("forgot.html")


@app.route("/list")
def lists():
    return render_template("list.html")


@app.route("/add")
def add():
    return render_template("add.html")


@app.route("/edit")
def edit():
    return render_template("edit.html")


@app.route("/account")
def account():
    return render_template("account.html")


if __name__ == "__main__":
    app.run()
