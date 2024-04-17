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
from typing import Dict, List,Tuple



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
    salt: Mapped[str] = mapped_column(String)

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
        self.user_to_room: Dict[str, int] = {}
        self.room_to_users: Dict[int, List[Tuple[str, bool]]] = {}


        
    

    def create_room(self, sender: str, receiver: str) -> int:
            room_id = self.counter.get()
            self.user_to_room[sender] = room_id
            self.user_to_room[receiver] = room_id
            self.room_to_users[room_id] = [(sender, True), (receiver, False)]
            return room_id
    
    def join_room(self, sender: str, room_id: int):
        if room_id not in self.room_to_users:
            raise ValueError(f"Invalid room ID {room_id}")
        if sender not in self.user_to_room:
            self.user_to_room[sender] = room_id
        self.room_to_users[room_id].append((sender, True))

    def leave_room(self, user: str):
        if user in self.user_to_room:
            room_id = self.user_to_room[user]
            self.room_to_users[room_id] = [(u, a) for u, a in self.room_to_users[room_id] if u != user]
            if not self.room_to_users[room_id]:
                del self.room_to_users[room_id]
            del self.user_to_room[user]

    def get_room_id(self, user: str):
        return self.user_to_room.get(user, None)

    def get_receiver(self, room_id: int, sender: str) -> str:
        if room_id in self.room_to_users:
            active_users = [user for user, active in self.room_to_users[room_id] if user != sender and active]
            if active_users:
                return active_users[0]
        return None


    