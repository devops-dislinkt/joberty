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


class Grade(db.Model, SerializerMixin):
    id: int = db.Column(db.Integer, primary_key=True)
    company_id: int = db.Column(db.Integer, db.ForeignKey("company.id"))
    user_id: int = db.Column(db.Integer, db.ForeignKey("user.id"))
    grade: int = db.Column(db.Integer, nullable=False)

    def __init__(self, fields: dict) -> None:
        # merge dictionaries
        self.__dict__ = {**self.__dict__, **fields}


class Comment(db.Model, SerializerMixin):

    id: int = db.Column(db.Integer, primary_key=True)
    company_id: int = db.Column(db.Integer, db.ForeignKey("company.id"))
    user_id: int = db.Column(db.Integer, db.ForeignKey("user.id"))
    description: str = db.Column(db.String(200), nullable=False)

    def __init__(self, fields: dict) -> None:
        # merge dictionaries
        self.__dict__ = {**self.__dict__, **fields}


class Company(db.Model, SerializerMixin):
    serialize_rules = ("-comments.company", "-grades.company")

    id: int = db.Column(db.Integer, primary_key=True)
    user_id: int = db.Column(db.Integer, db.ForeignKey("user.id"))
    approved: bool = db.Column(
        db.Boolean, default=False
    )  # approval for company registration
    name: str = db.Column(db.String(120), nullable=False)
    email: str = db.Column(db.String(120), nullable=False)
    location: str = db.Column(db.String(120), nullable=False)
    website: str = db.Column(db.String(120), nullable=False)
    description: str = db.Column(db.String(120), nullable=False)
    comments: list[Comment] = db.relationship("Comment", backref="company")
    grades: list[Grade] = db.relationship("Grade", backref="company")

    def __init__(self, fields: dict) -> None:
        # merge dictionaries
        self.__dict__ = {**self.__dict__, **fields}


class User(db.Model, SerializerMixin):
    serialize_rules = ("-company.user",)

    id: int = db.Column(db.Integer, primary_key=True)
    username: str = db.Column(db.String(80), unique=True, nullable=False)
    password: str = db.Column(db.String(200), unique=False, nullable=False)
    role: UserRole = db.Column(db.Enum(UserRole), default=UserRole.user, nullable=True)
    company: Company = db.relationship(
        "Company", uselist=False, backref="user", lazy=True
    )

    def __init__(self, fields: dict) -> None:
        # merge dictionaries
        self.__dict__ = {**self.__dict__, **fields}
