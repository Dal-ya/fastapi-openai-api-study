import os
import requests
from fastapi import APIRouter
import src.config.log as app_log
from dotenv import load_dotenv

from src.dto.dto import CreateGodlyCompletions, ApiResponse

load_dotenv()
logger = app_log.get_logger("godly_router")

router = APIRouter()


@router.get("")
async def root():
    return "hello godly api"


@router.post("/completions", status_code=200, response_model=ApiResponse)
async def completions(create_completions: CreateGodlyCompletions):
    try:
        url = os.environ["GODLY_COMPLETIONS_URL"]
        api_key = os.environ["GODLY_API_KEY"]
        payload = {
            "model": "gpt-3.5-turbo-0301",
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
            return {"success": True, "message": f"success to godly completions", "data": completion}
        else:
            print(response.text)
            logger.warning(response.status_code)
            raise Exception(f"fail code: {response.status_code}")

    except Exception as e:
        print(e)
        logger.error(e)
        return {"success": False, "message": f"fail to godly completions: {e}", "data": None}
