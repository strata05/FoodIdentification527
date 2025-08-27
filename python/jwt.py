
import random
from datetime import datetime, timezone, timedelta

from fastapi import HTTPException,status
from fastapi.params import Depends
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordBearer
from services.user_service import get_user

SECRET_KEY = "Dii3cainietheil8"
ALGORITHM = "HS256"

#
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
oauth2_scheme2 = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)

def generate_access_token(user_id: str, remember_me: bool) -> str:
    """

    :param user_id:
    :param remember_me:
    :return:
    """

    data = {
        "id": user_id,
        "exp": datetime.now(timezone.utc) + timedelta(days=30)
    }
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str = Depends(oauth2_scheme)):
    """

    :param token:
    :return:
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("id")
        exp = payload.get("exp")
        print("exp", exp)
        if not user_id or not exp or (exp < int(datetime.now(timezone.utc).timestamp())):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials 1",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user = get_user(user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials 2",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
