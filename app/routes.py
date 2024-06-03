from flask import Flask, Blueprint, render_template, request, redirect, url_for, session, jsonify, flash, current_app
from flask_login import login_user, logout_user, login_required
from .models import get_user_by_username, User, get_db_connection, generate_password
from .models import update_user_password, get_user_by_email
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
import itsdangerous

main = Blueprint('main', __name__)


# Configure Flask-Mail
def create_app():
    app = Flask(__name__)

    app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = 'xxxxxmail'
    app.config['MAIL_PASSWORD'] = 'xxxxxkey'
    app.config['MAIL_DEFAULT_SENDER'] = 'xxxxmail'
    mail = Mail(app)
    mail.init_app(app)
    return app


app = create_app()
mail = Mail(app)
mail.init_app(app)

# Secret key for token generation
app.config['SECRET_KEY'] = 'your-secret-key'
s = itsdangerous.URLSafeTimedSerializer(app.config['SECRET_KEY'])


@main.route("/", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        master_password = request.form['master_password']
        user_data = get_user_by_username(username)
        if user_data and check_password_hash(user_data['master_password'], master_password):
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
            hashed_password = generate_password_hash(master_password, method='pbkdf2:sha256', salt_length=16)
            db.execute('INSERT INTO users (username, email, master_password) VALUES (?, ?, ?)',
                       (username, email, hashed_password))
            db.commit()
            db.close()
            return redirect(url_for('main.login'))
    return render_template('register.html')


@main.route("/forgot", methods=['GET', 'POST'])
def forgot():
    if request.method == 'POST':
        email = request.form['email']
        user = get_user_by_email(email)
        if user:
            token = s.dumps(email, salt='password-reset-salt')
            link = url_for('main.reset_password', token=token, _external=True)
            msg = Message('Password Reset Request', sender=app.config['MAIL_USERNAME'], recipients=[email])
            msg.body = f'Your link to reset your password is {link}'
            mail.send(msg)
            flash('A password reset link has been sent to your email.', 'info')
        else:
            flash('Email address not found.', 'danger')
        return redirect(url_for('main.login'))
    return render_template("forgot.html")


@main.route("/reset/<token>", methods=['GET', 'POST'])
def reset_password(token):
    try:
        email = s.loads(token, salt='password-reset-salt', max_age=3600)
    except itsdangerous.SignatureExpired:
        flash('The password reset link has expired.', 'danger')
        return redirect(url_for('main.forgot'))
    except itsdangerous.BadSignature:
        flash('Invalid password reset link.', 'danger')
        return redirect(url_for('main.forgot'))

    if request.method == 'POST':
        new_password = request.form['master_password']
        re_new_password = request.form['re_master_password']
        if new_password == re_new_password:
            hashed_password = generate_password_hash(new_password, method='pbkdf2:sha256', salt_length=16)
            update_user_password(email, hashed_password)
            flash('Your password has been updated!', 'success')
            return redirect(url_for('main.login'))
        else:
            flash('Passwords do not match.', 'danger')
    return render_template('reset.html', token=token)


@main.route("/lists")
@login_required
def lists():
    db = get_db_connection()
    user_id = session['user_id']
    accounts = db.execute('SELECT * FROM accounts WHERE user_id = ?', (user_id,)).fetchall()
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
        user_id = session['user_id']
        db = get_db_connection()
        cur = db.cursor()
        cur.execute('INSERT INTO accounts (username, password, website, image, user_id) VALUES (?, ?, ?, ?, ?)',
                    (acc_username, password, website, image, user_id))
        db.commit()
        db.close()
        return redirect(url_for('main.lists'))
    return render_template("add.html")


# @main.route("/account/<int:account_id>")
# @login_required
# def account(account_id):
#     db = get_db_connection()
#     account = db.execute('SELECT * FROM accounts WHERE id = ?', (account_id,)).fetchone()
#     db.close()
#     return render_template("account.html", account=account)


@main.route("/edit<int:account_id>", methods=['GET', 'POST'])
@login_required
def edit(account_id):
    db = get_db_connection()
    user_id = session['user_id']
    account = db.execute('SELECT * FROM accounts WHERE id = ? AND user_id = ?', (account_id, user_id)).fetchone()
    if not account:
        db.close()
        return redirect(url_for('main.lists'))

    if request.method == 'POST':
        acc_username = request.form['acc_username']
        password = request.form['password'] or generate_password()
        website = request.form['website']
        image = request.form['image']
        db.execute(
            'UPDATE accounts SET username = ?, password = ?, website = ?, image = ? WHERE id = ? AND user_id = ?',
            (acc_username, password, website, image, account_id, user_id))
        db.commit()
        db.close()
        return redirect(url_for('main.lists'))
    db.close()
    return render_template('edit.html', account=account)


@main.route("/delete/<int:account_id>", methods=['POST'])
@login_required
def delete(account_id):
    db = get_db_connection()
    user_id = session['user_id']
    db.execute('DELETE FROM accounts WHERE id = ? AND user_id = ?', (account_id, user_id))
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
@login_required
def generate_password_route():
    password = generate_password()
    return jsonify(password=password)
