from typing import List
from fastapi import APIRouter
from src.dto.dto import CreateUserDto, ApiResponse
from src.models.user import User

router = APIRouter()


@router.get("/", status_code=200, response_model=ApiResponse[List[User]])
async def get_user_list():
    try:
        user_list = await User.find_all().to_list()
        return {"success": True, "message": "success get user list", "data": user_list}
    except Exception as e:
        print(e)
        return {"success": False, "message": "failed get user list", "data": None}


@router.post("/", status_code=201, response_model=ApiResponse[User])
async def create_user(user_create: CreateUserDto):
    try:
        user = await User(**user_create.dict()).insert()
        return {"success": True, "message": "success get user", "data": user}
    except Exception as e:
        print(e)
        return {"success": False, "message": "failed get user", "data": None}
