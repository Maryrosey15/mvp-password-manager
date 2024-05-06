from flask import Flask
from flask import render_template
from flask import request
import sqlite3

app = Flask(__name__, template_folder='src')


# Login Page
@app.route("/")
def login():
    return render_template("login.html")


# Register Page
@app.route("/register")
def register():
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
