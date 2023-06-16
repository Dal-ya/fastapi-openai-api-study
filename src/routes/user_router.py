from fastapi import Body, APIRouter, HTTPException

from src.models.user import User

router = APIRouter()


@router.get("/", status_code=200)
async def get_list():
    users = await User.find_all().to_list()
    return users


@router.post("/", status_code=201)
async def create_user(user: User):
    await user.create()
    return user
