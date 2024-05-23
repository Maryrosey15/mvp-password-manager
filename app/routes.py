from flask import Flask, Blueprint, render_template, request, redirect, url_for, session, jsonify, flash
from flask_login import login_user, logout_user, login_required
from app.models import get_user_by_username, User, get_db_connection, generate_password


main = Blueprint('main', __name__)


@main.route("/", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        master_password = request.form['master_password']
        user_data = get_user_by_username(username)
        if user_data and user_data['master_password'] == master_password:
            user = User(user_data['id'], user_data['username'], user_data['master_password'])
            login_user(user)
            return redirect(url_for('main.lists'))
        else:
            error = 'Invalid username or password'
            return render_template('login.html', error=error)
    return render_template("login.html")


@main.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        master_password = request.form['master_password']
        re_master_password = request.form['re_master_password']
        if master_password != re_master_password:
            error = 'Password do not match'
            return render_template('register.html', error=error)
        db = get_db_connection()
        existing_user = db.execute('SELECT id FROM users WHERE username = ?', (username,)).fetchone()
        if existing_user:
            error = 'Username already exists.'
            db.close()
            return render_template('register.html', error=error)
        else:
            db.execute('INSERT INTO users (username, email, master_password) VALUES (?, ?, ?)',
                       (username, email, master_password))
            db.commit()
            db.close()
            return redirect(url_for('main.login'))
    return render_template('register.html')


@main.route("/forgot")
def forgot():
    return render_template("forgot.html")


@main.route("/lists")
@login_required
def lists():
    db = get_db_connection()
    accounts = db.execute('SELECT * FROM accounts').fetchall()
    db.close()
    return render_template('list.html', accounts=accounts)


@main.route("/add", methods=['GET', 'POST'])
@login_required
def add():
    if request.method == 'POST':
        acc_username = request.form['acc_username']
        password = request.form['password'] or generate_password()
        website = request.form['website']
        image = request.form['image']
        db = get_db_connection()
        cur = db.cursor()
        cur.execute('INSERT INTO accounts (username, password, website, image) VALUES (?, ?, ?, ?)',
                    (acc_username, password, website, image))
        db.commit()
        db.close()
        return redirect(url_for('main.lists'))
    return render_template("add.html")


@main.route("/account/<int:account_id>")
@login_required
def account(account_id):
    db = get_db_connection()
    account = db.execute('SELECT * FROM accounts WHERE id = ?', (account_id,)).fetchone()
    db.close()
    return render_template("account.html", account=account)


@main.route("/edit<int:account_id>", methods=['GET', 'POST'])
@login_required
def edit(account_id):
    db = get_db_connection()
    account = db.execute('SELECT * FROM accounts WHERE id = ?', (account_id,)).fetchone()
    if request.method == 'POST':
        acc_username = request.form['acc_username']
        password = request.form['password'] or generate_password()
        website = request.form['website']
        image = request.form['image']
        db.execute('UPDATE accounts SET username = ?, password = ?, website = ?, image = ? WHERE id = ?',
                   (acc_username, password, website, image, account_id))
        db.commit()
        db.close()
        return redirect(url_for('main.lists'))
    db.close()
    return render_template('edit.html', account=account)


@main.route("/delete/<int:account_id>", methods=['POST'])
@login_required
def delete(account_id):
    db = get_db_connection()
    db.execute('DELETE FROM accounts WHERE id = ?', (account_id,))
    db.commit()
    db.close()
    return redirect(url_for('main.lists'))


@main.route("/logout")
@login_required
def logout():
    logout_user()
    session.pop('user_id', None)
    return redirect(url_for('main.login'))


@main.route("/generate_password")
def generate_password_route():
    password = generate_password()
    return jsonify(password=password)
