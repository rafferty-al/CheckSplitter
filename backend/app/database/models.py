from datetime import datetime
from pony import orm
from flask_login import UserMixin
from pony.orm import Database

db = Database()


class User(db.Entity, UserMixin):
    id = orm.PrimaryKey(int, auto=True)
    fullname = orm.Optional(str)
    password = orm.Required(str)
    nickname = orm.Optional(str)
    mastered_credits = orm.Set("Credit", reverse="master")
    slaved_credits = orm.Set("Credit", reverse="slave")
    sessions = orm.Set("UserInSession")
    credit_editions = orm.Set("CreditEdition", reverse="user")
    affected_editions = orm.Set("CreditEdition", reverse="affected_user")

    @property
    def virtual(self):
        return self.password is "None"

    def is_authenticated(self):
        return True

    @property
    def current_session(self):
        return orm.select(
            s.session for s in self.sessions if s.session.end is None
        ).first()


class Session(db.Entity):
    id = orm.PrimaryKey(int, auto=True)
    title = orm.Optional(str)
    orders = orm.Set("OrderedItem")
    users = orm.Set("UserInSession")
    start = orm.Optional(datetime)
    end = orm.Optional(datetime)


class OrderedItem(db.Entity):
    id = orm.PrimaryKey(int, auto=True)
    title = orm.Required(str)
    price = orm.Required(int)
    session = orm.Required(Session)
    user_in_sessions = orm.Set("UserInSession")


class Credit(db.Entity):
    id = orm.PrimaryKey(int, auto=True)
    master = orm.Required(User, reverse="mastered_credits")
    slave = orm.Required(User, reverse="slaved_credits")
    value = orm.Optional(int)
    credit_editions = orm.Set("CreditEdition")


class UserInSession(db.Entity):
    id = orm.PrimaryKey(int, auto=True)
    user = orm.Required(User)
    value = orm.Required(int, default=0)
    session = orm.Required(Session)
    orders = orm.Set(OrderedItem)


class CreditEdition(db.Entity):
    id = orm.PrimaryKey(int, auto=True)
    user = orm.Required(User, reverse="credit_editions")
    credit = orm.Required(Credit)
    old_value = orm.Required(int)
    new_value = orm.Required(int)
    affected_user = orm.Required(User, reverse="affected_editions")
