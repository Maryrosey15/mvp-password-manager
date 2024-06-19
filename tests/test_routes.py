from flask import url_for
from app.models import get_user_by_username, get_user_by_email, update_user_password
import itsdangerous


def test_register(client):
    response = client.post(url_for('main.register'), data={
        'username': 'testuser',
        'email': 'testuser@example.com',
        'master_password': 'StrongPassword1!',
        're_master_password': 'StrongPassword1!'
    }, follow_redirects=True)
    assert b'Login' in response.data
    assert get_user_by_username('testuser')

def test_login(client):
    response = client.post(url_for('main.login'), data={
        'username': 'testuser',
        'master_password': 'StrongPassword1!'
    }, follow_redirects=True)
    assert b'OTP' in response.data

def test_forgot_password(client):
    response = client.post(url_for('main.forgot'), data={
        'email': 'testuser@example.com'
    }, follow_redirects=True)
    assert b'password reset link has been sent' in response.data

def test_reset_password(client):
    # Simulate getting the token
    user = get_user_by_email('testuser@example.com')
    s = itsdangerous.URLSafeTimedSerializer('your-secret-key')
    token = s.dumps(user['email'], salt='password-reset-salt')

    response = client.post(url_for('main.reset_password', token=token), data={
        'master_password': 'NewStrongPassword1!',
        're_master_password': 'NewStrongPassword1!'
    }, follow_redirects=True)
    assert b'Your password has been updated' in response.data
    assert update_user_password(user['email'], 'NewStrongPassword1!')

def test_add_account(client, auth):
    auth.login()
    response = client.post(url_for('main.add'), data={
        'acc_username': 'testaccount',
        'password': 'password123',
        'website': 'example.com',
        'image': ''
    }, follow_redirects=True)
    assert b'Account list' in response.data
    assert b'testaccount' in response.data

def test_edit_account(client, auth):
    auth.login()
    response = client.post(url_for('main.edit', account_id=1), data={
        'acc_username': 'updatedaccount',
        'password': 'newpassword123',
        'website': 'newexample.com',
        'image': ''
    }, follow_redirects=True)
    assert b'Account list' in response.data
    assert b'updatedaccount' in response.data

def test_delete_account(client, auth):
    auth.login()
    response = client.post(url_for('main.delete', account_id=1), follow_redirects=True)
    assert b'Account list' in response.data
    assert b'updatedaccount' not in response.data
