'''
socket_routes
file containing all the routes related to socket.io
'''


from flask_socketio import join_room, emit, leave_room
from flask import request

try:
    from __main__ import socketio
except ImportError:
    from app import socketio

from models import Room

import db

room = Room()

# when the client connects to a socket
# this event is emitted when the io() function is called in JS
@socketio.on('connect')
def connect():
    username = request.cookies.get("username")
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
    room_id = request.cookies.get("room_id")
    if room_id is None or username is None:
        return
    emit("incoming", ("system", f"{username} has disconnected", "red", False), to=int(room_id))

# send message event handler
@socketio.on("send")
def send(username, message, signature, room_id):
    emit("incoming", (username, message, "black", True, signature), to=room_id)
    
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

    room_id = room.get_room_id(receiver_name)

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

@socketio.on('get_public_key')
def handle_get_public_key(username):
    user = db.get_user(username)
    if user:
        emit('public_key_response', {'public_key': user.pubKey})
    else:
        emit('public_key_response', {'error': 'User not found'})

@socketio.on('get_private_key')
def handle_get_private_key(username):
    user = db.get_user(username)
    if user:
        emit('private_key_response', {'private_key': user.priKey})
    else:
        emit('private_key_response', {'error': 'User not found'})