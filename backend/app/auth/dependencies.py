from app.auth.security import decode_access_token
from app.database.database import get_db
from app.models.user import User
from fastapi import Depends, HTTPException, status
#from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/token"
)

#security = HTTPBearer()


# def get_current_user(
#     credentials: HTTPAuthorizationCredentials = Depends(security),  # noqa: B008
#     db: Session = Depends(get_db),  # noqa: B008
# ):

def get_current_user(
    token: str = Depends(oauth2_scheme),  # noqa: B008
    db: Session = Depends(get_db),  # noqa: B008
):
    #token = credentials.credentials

    username = decode_access_token(token)

    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    user = db.query(User).filter(
        User.username == username
    ).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user