'''
socket_routes
file containing all the routes related to socket.io
'''

import os
import json
from flask_socketio import join_room, emit, leave_room
from flask import request

try:
    from __main__ import socketio
except ImportError:
    from app import socketio

from models import Room

import db

room = Room()
online_users = set()
# when the client connects to a socket
# this event is emitted when the io() function is called in JS
@socketio.on('connect')
def connect():
    username = request.cookies.get("username")
    if username:
        online_users.add(username)
    room_id = request.cookies.get("room_id")
    if room_id is None or username is None:
        return
    # socket automatically leaves a room on client disconnect
    # so on client connect, the room needs to be rejoined
    join_room(int(room_id))
    emit("incoming", ("system", f"{username} has connected", "green", False), to=int(room_id))

# event when client disconnects
# quite unreliable use sparingly
@socketio.on('disconnect')
def disconnect():
    username = request.cookies.get("username")
    if username:
        online_users.remove(username)
    room_id = request.cookies.get("room_id")
    if room_id is None or username is None:
        return
    emit("incoming", ("system", f"{username} has disconnected", "red", False), to=int(room_id))

# send message event handler
@socketio.on("send")
def send(username, message, signature, room_id):
    receiver = room.get_receiver_name(room_id, username)  
    if receiver not in online_users:
        emit("incoming", ("system", "The receiver is off-line", "red", False))
        return
    emit("incoming", (username, message, "black", True, signature), to=room_id)
    
'''
#For testing message modification
import base64
@socketio.on("send")
def send(username, message, signature, room_id):
    modified_message = "1"
    #encoded_modified_message = base64.b64encode(modified_message.encode('utf-8')).decode('utf-8')
    
    emit("incoming", (username, modified_message, "black", True, signature), to=room_id)
'''

# join room event handler
# sent when the user joins a room
@socketio.on("join")
def join(sender_name, receiver_name):
    
    receiver = db.get_user(receiver_name)
    if receiver is None:
        return "Unknown receiver!"
    
    sender = db.get_user(sender_name)
    if sender is None:
        return "Unknown sender!"
    
    friends = db.get_all_friends_of_current_user(sender_name)
    if receiver_name not in friends:
        return "Not a friend!"
    
    file_path = f"messages/{sender_name}_to_{receiver_name}.json"
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
        for message in data:
            sender = message.get("sender", "")
            message_text = message.get("message", "")
            color = message.get("color", "")
            emit("history", (sender, message_text, color, True))
    except FileNotFoundError:
        pass

    room_id = room.get_room_id(receiver_name) # get receiver's room id
    # if the user is already inside of a room 
    if room_id is not None:
        
        room.join_room(sender_name, room_id)
        join_room(room_id)
        # emit to everyone in the room except the sender
        emit("incoming", ("system", f"{sender_name} has joined the room.", "green", False), to=room_id, include_self=False)
        # emit only to the sender
        emit("incoming", ("system", f"{sender_name} has joined the room. Now talking to {receiver_name}.", "green", False))
        return room_id

    # if the user isn't inside of any room, 
    # perhaps this user has recently left a room
    # or is simply a new user looking to chat with someone
    room_id = room.create_room(sender_name, receiver_name)
    join_room(room_id)
    emit("incoming", ("system", f"{sender_name} has joined the room. Now talking to {receiver_name}.", "green", False), to=room_id)
    return room_id

# leave room event handler
@socketio.on("leave")
def leave(username, room_id):
    emit("incoming", ("system", f"{username} has left the room.", "red", False), to=room_id)
    leave_room(room_id)
    room.leave_room(username)

# Below are new functions

@socketio.on('get_public_key_for_send')
def handle_get_public_key_for_send(username):
    user = db.get_user(username)
    if user:
        emit('public_key_response_for_send', {'public_key': user.pubKey})
    else:
        emit('public_key_response_for_send', {'error': 'User not found'})

@socketio.on('get_public_key_for_check')
def handle_get_public_key_for_check(username):
    user = db.get_user(username)
    if user:
        emit('public_key_response_for_check', {'public_key': user.pubKey})
    else:
        emit('public_key_response_for_check', {'error': 'User not found'})

@socketio.on('get_public_key_for_save')
def handle_get_public_key_for_save(username):
    user = db.get_user(username)
    if user:
        emit('public_key_response_for_save', {'public_key': user.pubKey})
    else:
        emit('public_key_response_for_save', {'error': 'User not found'})

@socketio.on('get_private_key')
def handle_get_private_key(username):
    user = db.get_user(username)
    if user:
        emit('private_key_response', {'private_key': user.priKey})
    else:
        emit('private_key_response', {'error': 'User not found'})

@socketio.on('save_message')
def save_message_on_server(message, room_sender, room_receiver, sender, color):
    # create the folder
    folder_path = 'messages'
    os.makedirs(folder_path, exist_ok=True)
    
    file_path = f'{folder_path}/{room_sender}_to_{room_receiver}.json'
    
    data = {
        "sender": sender,
        "message": message,
        "color": color,
    }
    
    # check/create the file
    if not os.path.isfile(file_path):
        with open(file_path, 'w') as file:
            json.dump([data], file, indent=4)
    else:
        with open(file_path, 'r+') as file:
            file_contents = json.load(file) # read existing data
            file_contents.append(data)
            file.seek(0)
            json.dump(file_contents, file, indent=4)
            file.truncate() # delete original content