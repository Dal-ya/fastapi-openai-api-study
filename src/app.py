from fastapi import FastAPI
from src.routes.user_router import router as user_router
from src.config.database import initiate_database


app = FastAPI()


@app.on_event("startup")
async def start_database():
    await initiate_database()


@app.get("/")
def read_root():
    return {"Hello": "World"}


app.include_router(user_router, tags=["user"], prefix="/api/user")
