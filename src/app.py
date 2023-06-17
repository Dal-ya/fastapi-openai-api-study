from fastapi import FastAPI, Response, Request
from src.routes.user_router import router as user_router
from src.config.database import initiate_database
import src.config.log as app_log


# setup log
logger = app_log.get_logger("app_main")

# setup app
app = FastAPI()


@app.on_event("startup")
async def start_database():
    await initiate_database()


@app.get("/")
def read_root():
    return {"Hello": "World"}


app.include_router(user_router, tags=["user"], prefix="/api/user")

# request/response logging
# https://stackoverflow.com/questions/69670125/how-to-log-raw-http-request-response-in-python-fastapi
"""
from starlette.background import BackgroundTask
from starlette.types import Message

def log_info(req_body, res_body):
    logger.info(req_body)
    logger.info(res_body)


async def set_body(request: Request, body: bytes):
    async def receive() -> Message:
        return {'type': 'http.request', 'body': body}

    request._receive = receive


@app.middleware('http')
async def some_middleware(request: Request, call_next):
    req_body = await request.body()
    await set_body(request, req_body)
    response = await call_next(request)

    res_body = b''
    async for chunk in response.body_iterator:
        res_body += chunk

    task = BackgroundTask(log_info, req_body, res_body)
    return Response(content=res_body, status_code=response.status_code,
                    headers=dict(response.headers), media_type=response.media_type, background=task)
"""
