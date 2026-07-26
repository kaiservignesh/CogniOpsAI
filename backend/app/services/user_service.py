from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.user import User


def get_all_users(db: Session):
    return db.query(User).all()


# def create_user(db, user):
#     db_user = User(
#         username=user.username,
#         email=user.email,
#     )
#     db.add(db_user)
#     db.commit()
#     db.refresh(db_user)
#     return db_user

def create_user(db: Session, user):
    existing_user = (
        db.query(User)
        .filter(User.username == user.username)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=409,
            detail="Username already exists"
        )

    existing_email = (
        db.query(User)
        .filter(User.email == user.email)
        .first()
    )

    if existing_email:
        raise HTTPException(
            status_code=409,
            detail="Email already exists"
        )

    db_user = User(
        username=user.username,
        email=user.email,
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user