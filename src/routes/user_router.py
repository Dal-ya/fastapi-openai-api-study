import os
from typing import List
from fastapi import APIRouter, Depends
from src.dto.dto import CreateUserDto, ApiResponse, UserSignInDto
from src.jwt.handler import sign_jwt
from src.models.user import User
import src.config.log as app_log
from dotenv import load_dotenv
from passlib.context import CryptContext
from src.jwt.bearer import JWTBearer

load_dotenv()
logger = app_log.get_logger("user_router")
crypto = CryptContext(schemes=["bcrypt"])

router = APIRouter()

# jwt bearer
jwt_bearer = JWTBearer()


@router.get("/list", status_code=200, response_model=ApiResponse[List[User]], dependencies=[Depends(jwt_bearer)])
async def get_user_list():
    # TODO: current jwt test fn ==> will add logic "remove response filed password" and "pagination query"
    """
    유저 목록 가져오기 
    """
    try:
        user_list = await User.find_all().to_list()
        return {"success": True, "message": "success get user list", "data": user_list}
    except Exception as e:
        print(e)
        logger.error(e)
        return {"success": False, "message": "failed get user list", "data": None}


@router.post("", status_code=200, response_model=ApiResponse[User])
async def create_user(user_create: CreateUserDto):
    """
    유저 생성하기
    """
    try:
        if user_create.secret != os.environ["CREATE_USER_KEY"]:
            return {"success": False, "message": "secret key is not valid", "data": None}

        if await User.find_one(User.email == user_create.email):
            return {"success": False, "message": "email is already exist", "data": None}

        user_create.password = crypto.hash(user_create.password)
        user = await User(**user_create.dict()).insert()
        filtered_user = {key: value for key, value in user.dict().items() if key != "password"}

        return {"success": True, "message": "success get user", "data": filtered_user}
    except Exception as e:
        print(e)
        logger.error(e)
        return {"success": False, "message": "failed get user", "data": None}


@router.post("/sign-in", status_code=200, response_model=ApiResponse[User])
async def sign_in(user_sign_in: UserSignInDto):
    """
    유저 로그인
    """
    try:
        user = await User.find_one(User.email == user_sign_in.email)
        if user is None:
            return {"success": False, "message": "user is not exist", "data": None}

        if not crypto.verify(user_sign_in.password, user.password):
            return {"success": False, "message": "email or password is not valid", "data": None}

        return {"success": True, "message": "success signin user", "data": sign_jwt(user.email)}
    except Exception as e:
        print(e)
        logger.error(e)
        return {"success": False, "message": "failed get user", "data": None}
