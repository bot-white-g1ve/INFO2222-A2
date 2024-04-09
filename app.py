'''
app.py contains all of the server application
this is where you'll find all of the get/post request handlers
the socket event handlers are inside of socket_routes.py
'''

from flask import Flask, render_template, request, abort, url_for, redirect, session
from flask_socketio import SocketIO
from werkzeug.security import generate_password_hash, check_password_hash

import db
import secrets
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes

# import logging

# this turns off Flask Logging, uncomment this to turn off Logging
# log = logging.getLogger('werkzeug')
# log.setLevel(logging.ERROR)

app = Flask(__name__)

# secret key used to sign the session cookie
app.config['SECRET_KEY'] = secrets.token_hex()
socketio = SocketIO(app)

# don't remove this!!
import socket_routes

# index page
@app.route("/")
def index():
    return render_template("index.jinja")


# login page
@app.route("/login")
def login():
    return render_template("login.jinja")


# handles a post request when the user clicks the log in button
@app.route("/login/user", methods=["POST"])
def login_user():
    if not request.is_json:
        abort(404)

    username = request.json.get("username")
    password = request.json.get("password")

    user = db.get_user(username)
    if user is None:
        return "Error: User does not exist!"

    if user.password != password:
        return "Error: Password does not match!"
    
    session['username'] = username
    session['logged_in'] = True

    return url_for('home', username=request.json.get("username"))

# handles a get request to the signup page
@app.route("/signup")
def signup():
    return render_template("signup.jinja")

# handles a post request when the user clicks the signup button
@app.route("/signup/user", methods=["POST"])
def signup_user():
    if not request.is_json:
        abort(404)
    username = request.json.get("username")
    password = request.json.get("password")
    public_key = request.json.get("publicKey")
    private_key = request.json.get("privateKey")
    
    if username == "system":
        return "Error: Invalid username!"
    
    if db.get_user(username) is None:
        db.insert_user(username, password, public_key, private_key)
        return url_for('home', username=username)
    return "Error: User already exists!"


# handler when a "404" error happens
@app.errorhandler(404)
def page_not_found(_):
    return render_template('404.jinja'), 404

# home page, where the messaging app is
@app.route("/home")
def home():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    if request.args.get("username") is None:
        abort(404)

    username = session.get("username")
    #FIXME 设置session,记录当前登录用户信息
    session['current_user'] = username
    session.permanent = True
    # FIXME 找到当前用户所有的朋友， 并交给模板宣染
    friends = db.get_all_friends_of_current_user(username)
    requests = db.get_all_request(username)
    return render_template("home.jinja", username=session.get("username"), friends=friends, requests = requests)


@app.route("/add_friend")
def add_friend():
    if request.args.get("friend_name") is None:
        return f"need a friend username"
    #FIXME 从当前会话中获取登录用户信息
    current_user = session.get('current_user', None)
    if current_user is None:
        return "session expired, try to re-log in"
    friend_name = request.args.get("friend_name")
    if friend_name == current_user:
        return "You can't send request to yourself"
    
    success = db.request_friend(current_user, friend_name )
    if success:
        return f"successful to send the friend request to {friend_name}"
    else:
        return f"failed to send the friend request to {friend_name}"
    
@app.route("/reject_friend")
def reject_friend():
    current_user = session.get('current_user', None)
    if current_user is None:
        return "session expired, try to re-log in"
    friend_name = request.args.get("friend_name")
    db.rejected_friend(current_user, friend_name )
    return f"rejected {friend_name}"

@app.route("/accept_friend")
def accept_friend():
    current_user = session.get('current_user', None)
    if current_user is None:
        return "session expired, try to re-log in"
    friend_name = request.args.get("friend_name")
    success = db.accept_friend(current_user, friend_name )
    if success:
        return f"successfully accepted the request from {friend_name}"
    else:
        return f"unable to accepet request."

if __name__ == '__main__':
    socketio.run(app)
