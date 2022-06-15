from typing import Literal
from app import db
from sqlalchemy_serializer import SerializerMixin
import enum


class UserRole(enum.Enum):
    admin = 1
    user = 2
    company_owner = 3
    
    def __str__(self):
        return str(self.value)

class User(db.Model, SerializerMixin):
    id:int = db.Column(db.Integer, primary_key=True)
    username:str = db.Column(db.String(80), unique=True, nullable=False)
    password: str = db.Column(db.String(80), unique=False, nullable=False)
    role: UserRole = db.Column(db.Enum(UserRole), default=UserRole.user)