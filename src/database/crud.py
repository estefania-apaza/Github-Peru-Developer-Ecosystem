from sqlalchemy.orm import Session
from .models import User, Repository, Classification

def create_user(db: Session, user_data: dict):
    db_user = User(**user_data)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(User).offset(skip).limit(limit).all()

def create_repository(db: Session, repo_data: dict, owner_id: int):
    db_repo = Repository(**repo_data, owner_id=owner_id)
    db.add(db_repo)
    db.commit()
    db.refresh(db_repo)
    return db_repo

def update_classification(db: Session, repo_id: int, class_data: dict):
    db_class = db.query(Classification).filter(Classification.repo_id == repo_id).first()
    if db_class:
        for key, value in class_data.items():
            setattr(db_class, key, value)
    else:
        db_class = Classification(**class_data, repo_id=repo_id)
        db.add(db_class)
    db.commit()
    return db_class