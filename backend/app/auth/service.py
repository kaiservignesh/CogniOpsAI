from sqlalchemy.orm import Session

from app.auth.security import create_access_token, verify_password
from app.models.user import User


def authenticate_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()

    if not user:
        return None

    if not verify_password(password, user.hashed_password):
        return None

    access_token = create_access_token(
        data={"sub": user.username}
    )

    return access_token