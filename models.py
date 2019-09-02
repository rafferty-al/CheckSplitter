from datetime import datetime
from pony.orm import *


db = Database()


class User(db.Entity):
    id = PrimaryKey(int, auto=True)
    fullname = Optional(str)
    nickname = Optional(str)
    sessions = Set('Session')
    orders = Set('OrderedItem')
    mastered_credits = Set('Credit', reverse='master')
    slaved_credits = Set('Credit', reverse='slave')
    session_maintains = Set('SessionMaintain')


class Session(db.Entity):
    id = PrimaryKey(int, auto=True)
    users = Set(User)
    orders = Set('OrderedItem')
    session_maintains = Set('SessionMaintain')
    start = Optional(datetime)
    end = Optional(datetime)


class OrderedItem(db.Entity):
    id = PrimaryKey(int, auto=True)
    title = Required(str)
    price = Required(int)
    session = Required(Session)
    users = Set(User)


class Credit(db.Entity):
    id = PrimaryKey(int, auto=True)
    master = Required(User, reverse='mastered_credits')
    slave = Required(User, reverse='slaved_credits')


class SessionMaintain(db.Entity):
    id = PrimaryKey(int, auto=True)
    user = Required(User)
    value = Required(int)
    session = Required(Session)


db.bind('sqlite', 'db.sqlite', create_db=True)