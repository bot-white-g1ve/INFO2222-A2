'''
models
defines sql alchemy data models
also contains the definition for the room class used to keep track of socket.io rooms

Just a sidenote, using SQLAlchemy is a pain. If you want to go above and beyond, 
do this whole project in Node.js + Express and use Prisma instead, 
Prisma docs also looks so much better in comparison

or use SQLite, if you're not into fancy ORMs (but be mindful of Injection attacks :) )
'''

from sqlalchemy import String,Column,Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.declarative import declarative_base
from typing import Dict, Set



Base =  declarative_base()

class Base(DeclarativeBase):
    pass

# data models
# model to store user information
class User(Base):
    __tablename__ = "user"
    username: Mapped[str] = mapped_column(String, primary_key=True)
    password: Mapped[str] = mapped_column(String)
    pubKey: Mapped[str] = mapped_column(String)
    priKey: Mapped[str] = mapped_column(String)

class Friendship(Base):
    __tablename__ = "friendships"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user1: Mapped[str] = mapped_column(String)
    user2: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String,default="rejected")#accepted/requested/rejected

    
    
    
# stateful counter used to generate the room id
class Counter():
    def __init__(self):
        self.counter = 0
    
    def get(self):
        self.counter += 1
        return self.counter

# Room class, used to keep track of which username is in which room
class Room():
    def __init__(self):
        self.counter = Counter()
        # dictionary that maps the username to the room id
        # for example self.dict["John"] -> gives you the room id of 
        # the room where John is in
        self.dict: Dict[str, int] = {}
        self.room_to_users: Dict[int, Set[str]] = {}

    def create_room(self, sender: str, receiver: str) -> int:
        room_id = self.counter.get()
        self.dict[sender] = room_id
        self.dict[receiver] = room_id
        if room_id in self.room_to_users:
            self.room_to_users[room_id].update([sender, receiver])
        else:
            self.room_to_users[room_id] = {sender, receiver}
        return room_id
    
    def join_room(self,  sender: str, room_id: int) -> int:
        self.dict[sender] = room_id
        if room_id in self.room_to_users:
            self.room_to_users[room_id].add(sender)
        else:
            self.room_to_users[room_id] = {sender}


    def leave_room(self, user):
        room_id = self.dict[user]
        if user not in self.dict.keys():
            return
        del self.dict[user]
        self.room_to_users[room_id].remove(user)

    # gets the room id from a user1
    def get_room_id(self, user: str):
        if user not in self.dict.keys():
            return None
        return self.dict[user]
    
    def get_receiver_name(self, room_id: int, username: str):
        users_in_room = self.room_to_users.get(room_id)
        if users_in_room:
            for user in users_in_room:
                if user != username:
                    return user
        return None
    
