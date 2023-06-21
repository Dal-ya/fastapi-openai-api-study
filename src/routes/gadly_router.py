import os
import requests
from fastapi import APIRouter
import src.config.log as app_log
from dotenv import load_dotenv

from src.dto.dto import CreateGadlyCompletions

load_dotenv()
logger = app_log.get_logger("gadly_router")

router = APIRouter()


@router.get("/")
async def root():
    return "hello gadly api"


@router.post("/completions", status_code=200)
async def completions(create_completions: CreateGadlyCompletions):
    try:
        url = os.environ["GADLY_COMPLETIONS_URL"]
        api_key = os.environ["GADLY_API_KEY"]
        payload = {
            "model": "gpt-3.5-turbo",
            "max_total_matches_tokens": create_completions.maxTotalMatchesTokens,
            "prompt": create_completions.prompt,
        }
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": f"Bearer {api_key}"
        }

        response = requests.post(url, json=payload, headers=headers)

        if response.status_code == 200:
            completion = response.json()["choices"][0]["message"]["content"]
            return {"success": True, "message": f"success to gadly completions", "data": completion}
        else:
            print(response.text)
            logger.warning(response.status_code)
            raise Exception(f"fail code: {response.status_code}")

    except Exception as e:
        print(e)
        logger.error(e)
        return {"success": False, "message": f"fail to gadly completions: {e}", "data": None}
