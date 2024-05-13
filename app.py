from flask import Flask
from flask import render_template, request, url_for, session, redirect, flash, g
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3

from flask_login import LoginManager

login_manager = LoginManager()

app: Flask = Flask(__name__, template_folder='src')

app.secret_key = "har199"

# Configure SQLite database
app.config['DATABASE'] = 'database.db'


def get_db_connection():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn


def close_db_connection():
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.before_request
def before_request():
    g.db = get_db_connection()


@app.teardown_request
def teardown_request(exception):
    close_db_connection()


def get_user_by_username(username):
    cursor = g.db.execute('SELECT * FROM users WHERE username = ?', (username,))
    return cursor.fetchone()


def init_db():
    with app.app_context():
        db = get_db_connection()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


# Login Page
@app.route("/", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        master_password = request.form['master_password']

        user = get_user_by_username(username)
        if user and user['master_password'] == master_password:
            session['user_id'] = user['id']
            return redirect(url_for('lists'))
        else:
            error = 'Invalid username or password'
            return render_template('login.html', error=error)

    return render_template("login.html")


# Register Page
@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        master_password = request.form['master_password']
        re_master_password = request.form['re_master_password']

        if master_password != re_master_password:
            error = 'Password do not match'
            return render_template('register.html', error=error)

        db = get_db_connection()
        existing_user = db.execute('SELECT id FROM users WHERE username = ?',
                                   (username,)).fetchone()
        if existing_user:
            error = 'Username already exist.'
            db.close()
            return render_template('register.html', error=error)
        else:
            db.execute('INSERT INTO users (username, master_password) VALUES (?,?)',
                       (username, master_password))
            db.commit()
            db.close()
            return redirect(url_for('login'))
    return render_template('register.html')


@app.route("/forgot")
def forgot():
    return render_template("forgot.html")


@app.route("/lists")
def lists():
    # if 'user_id' in session:
    #     # code here to fetch account data from database

    #     return render_template('list.html')
    # else:
    #     return render_template("login.html")
    return render_template('list.html')


@app.route("/add")
def add():
    if request.method == 'POST':
        username = request.form('username')
        password = request.form('password')
        website = request.form('website')
        image = request.form('image')

        db = get_db_connection()
        cur = db.cursor()
        cur.execute('INSERT INTO users (username, password, website, image) VALUES (?,?,?,?)', (username, password, website, image))
        db.commit()
        db.close()

        return redirect(url_for('lists'))

    return render_template("add.html")


@app.route("/edit")
def edit():
    return render_template("edit.html")


@app.route("/account")
def account():
    return render_template("account.html")


@app.route("/logout")
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))


init_db()


if __name__ == "__main__":
    app.run(debug=True)
