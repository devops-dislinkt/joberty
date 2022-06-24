from typing import Optional, TypeVar
from .models import User, db, Comment
from flask import current_app
from sqlalchemy.exc import SQLAlchemyError

T = TypeVar("T")


def get_all(model: T) -> list[T]:
    data = model.query.all()
    return data


def add_or_update(instance: T) -> T:
    ret = db.session.merge(instance)
    commit_changes()
    return ret


def delete_instance(model, id: int):
    model.query.filter_by(id=id).delete()
    commit_changes()


def edit_instance(model, id, fields: dict):
    instance = model.query.filter_by(id=id).first()
    for attr, new_value in fields.items():
        setattr(instance, attr, new_value)
    commit_changes()


def find_by_username(username: str) -> Optional[User]:
    """Finds User by username. If User object is not found, None is returned."""
    return User.query.filter_by(username=username).first()

def find_by_company_id(id):
    return Comment.query.filter_by(company_id=id)

def find_by_id(model: T, id) -> T:
    return model.query.get(id)


def commit_changes():
    try:
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(e)
        raise e
