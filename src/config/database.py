import os
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from src.models.user import User
from dotenv import load_dotenv

load_dotenv()


async def initiate_database():
    client = AsyncIOMotorClient(
        os.environ["DATABASE_URL"]
    )
    await init_beanie(
        database=client.db_name,
        document_models=[User]
    )
