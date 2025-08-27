from datetime import datetime, timezone

import ulid
from fastapi import APIRouter
from fastapi.params import Depends
from pydantic import BaseModel
import re
import dao.user_dao as user_dao
from jwt import generate_access_token, verify_token
from models.user import User
import bcrypt

router = APIRouter()

#
class RegisterRequest(BaseModel):
    email: str
    password: str
    username: str

#
class LoginRequest(BaseModel):
    email: str
    password: str
    remember_me: bool = False

#
# class UserLittleProfileResponse(BaseModel):
#     id: str
#     nickname: str
#     avatar: str | None
#
#
#

def is_valid_email(email: str) -> bool:
    """

    :param email:
    :return:
    """
    if not email:
        return False

    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

def is_valid_password(password: str) -> bool:
    """

    :param password:
    :return:
    """
    if not password:
        return False
    if len(password) < 8 or len(password) > 32:
        return False
    return True

def is_valid_username(username: str) -> bool:
    """

    :param username:
    :return:
    """
    if not username:
        return False
    if len(username) < 2 or len(username) > 32:
        return False
    return True

@router.post("/register")
async def register(data: RegisterRequest):
    """

    :param data:
    :return:
    """

    if not is_valid_email(data.email):
        return {"error": "Invalid email", "error_code": 1001}
    if not is_valid_password(data.password):
        return {"error": "Invalid password", "error_code": 1001}
    if not is_valid_username(data.username):
        return {"error": "Invalid username", "error_code": 1001}

    # checking existing user
    if user_dao.find_user_by_email(data.email) is not None:
        return {"error": "User already exists", "error_code": 1002}

    now_ms = int(datetime.now(timezone.utc).timestamp() * 1000)  #
    user = User(
        u_id=str(ulid.ULID()),
        email=data.email,
        username=data.username,
        password=bcrypt.hashpw(data.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
        created_at=now_ms,
        updated_at=now_ms
    )

    try:
        user_dao.insert_user(user)
        return {"success": True}
    except Exception as e:
        return {"error": "Server Error" + str(e), "error_code": 1003}



@router.post("/login")
async def login(data: LoginRequest):
    """

    :param data:
    :return:
    """

    if not is_valid_email(data.email):
        return {"error": "Invalid email", "error_code": 1003}
    if not is_valid_password(data.password):
        return {"error": "Invalid password", "error_code": 1003}

    user = user_dao.find_user_by_email(data.email)
    if user is None:
        return {"error": "Email or password error", "error_code": 1004}

    if not bcrypt.checkpw(data.password.encode('utf-8'), user.password.encode('utf-8')):
        return {"error": "Email or password error", "error_code": 1004}

    return {"success": True, "token": generate_access_token(user.u_id, data.remember_me)}


@router.get("/info")
async def get_user_info(current_user: User = Depends(verify_token)):
    """

    :param current_user:
    :return:
    """

    return {"success": True, "user": current_user.model_dump(exclude={"password", "created_at", "updated_at"})}
#
# @router.get("/logout")
# async def user_logout(current_user: User = Depends(verify_token)):
#     """
#
#     :param current_user:
#     :return:
#     """
#
#     return {"success": True}
#
