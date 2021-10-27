import typing
from datetime import datetime

from pydantic import BaseModel, validator

from app.schemas.auth import BaseError
from backend.app.startup import db


class BaseSchema(BaseModel):
    class Config:
        orm_mode = True
        json_encoders = {
            datetime: lambda v: v.strftime("%Y-%m-%d %H:%M:%S"),
        }


class SessionError(BaseError):
    pass


class UserSchema(BaseSchema):
    fullname: str
    nickname: str


class UserInSessionSchema(BaseSchema):
    id: int
    nickname: str
    value: int


class LogSchema(BaseSchema):
    debtor: UserInSessionSchema
    creditor: UserInSessionSchema
    value: int


class OrderSchema(BaseSchema):
    title: str
    price: int
    users: typing.List[UserSchema]


class SessionResponseSchema(BaseSchema):
    title: str
    start: datetime
    end: typing.Optional[datetime]
    order_items: typing.Optional[typing.List[OrderSchema]]
    user_items: typing.Optional[typing.List[UserSchema]]


class SessionUpdateRequestSchema(BaseSchema):
    title: typing.Optional[str]
    end_session: typing.Optional[bool]
