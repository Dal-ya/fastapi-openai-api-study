from fastapi import FastAPI
from src.routes.user_router import router as user_router
from src.config.database import initiate_database
import src.config.log as app_log

# setup log
logger = app_log.get_logger(__name__)
print('logger: ', logger)
print('name: ', __name__)

app = FastAPI()


@app.on_event("startup")
async def start_database():
    await initiate_database()


@app.get("/")
def read_root():
    logger.error("test logger!")
    return {"Hello": "World"}


app.include_router(user_router, tags=["user"], prefix="/api/user")
