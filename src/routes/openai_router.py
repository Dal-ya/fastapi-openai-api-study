from fastapi import APIRouter, UploadFile, Form
import src.config.log as app_log
from src.dto.dto import ApiResponse, RequestChatByFineTuneDTO, CreatePaintDTO

from src.utils.openai_util import get_file_list, get_fine_tune_list, fine_tune_save_file, create_jsonl, upload_jsonl, \
    create_fine_tune_model, chat_by_fine_tune_model, delete_fine_tune_model, translate_description, generate_image

logger = app_log.get_logger("openai_router")
router = APIRouter()


# TODO: Check the ApiResponse[??] ?? Data Type
@router.get('/list-file', response_model=ApiResponse)
async def list_file():
    """
    OpenAI에 업로드한 파일 목록 가져오기
    """
    try:
        get_file_list_result = get_file_list()
        if not get_file_list_result["success"]:
            print(get_file_list_result["message"])
            raise Exception("-")

        return {
            "success": True,
            "message": "success to get file list",
            "data": get_file_list_result["data"]
        }

    except Exception as e:
        print(e)
        logger.error(e)
        return {"success": False, "message": f"fail to get file list, {e}", "data": None}


@router.get('/list-fine-tune', response_model=ApiResponse)
async def list_fine_tune():
    """
    생성한 파인 튜닝 모델 목록 가져오기
    """
    try:
        get_fine_tune_list_result = get_fine_tune_list()
        if not get_fine_tune_list_result["success"]:
            print(get_fine_tune_list_result["message"])
            raise Exception("-")

        return {
            "success": True,
            "message": "success to get fine tune list",
            "data": get_fine_tune_list_result["data"]
        }

    except Exception as e:
        print(e)
        logger.error(e)
        return {"success": False, "message": f"fail to get fine tune list, {e}", "data": None}


@router.post('/create-fine-tune', response_model=ApiResponse)
async def create_fine_tune(file: UploadFile, modelName: str = Form(...)):
    """
    파인 튜닝 모델 생성하기
    """
    try:
        # 텍스트 파일 저장
        fine_tune_save_file_result = await fine_tune_save_file(file)
        if not fine_tune_save_file_result["success"]:
            print(fine_tune_save_file_result["message"])
            raise Exception("fail to save file")

        file_name = fine_tune_save_file_result["data"]["fileName"]
        file_path = fine_tune_save_file_result["data"]["filePath"]

        # jsonl 파일 생성
        create_jsonl_result = create_jsonl(file_name, file_path)
        if not create_jsonl_result["success"]:
            print(create_jsonl_result["message"])
            raise Exception("fail to create jsonl")

        # jsonl 파일 업로드
        upload_jsonl_result = upload_jsonl(create_jsonl_result["data"]["filePath"])
        if not upload_jsonl_result["success"]:
            print(upload_jsonl_result["message"])
            raise Exception("fail to upload jsonl")

        # fine tune 모델 생성
        create_fine_tune_model_result = create_fine_tune_model(upload_jsonl_result["data"]["fileId"], modelName)
        if not create_fine_tune_model_result["success"]:
            print(create_fine_tune_model_result["message"])
            raise Exception("fail to create fine tune")

        return {
            "success": True,
            "message": "success to create fine tune",
            "data": {}
        }

    except Exception as e:
        print(e)
        logger.error(e)
        return {"success": False, "message": f"fail to create fine tune, {e}", "data": None}


@router.post('/completion-by-fine-tune', response_model=ApiResponse)
async def completion_by_fine_tune(body: RequestChatByFineTuneDTO):
    """
    파인 튜닝 모델을 이용해서 컴플리션(completion) 데이터 받기
    """
    try:
        chat_by_fine_tune_model_result = chat_by_fine_tune_model(body.fineTuneModel, body.prompt)
        if not chat_by_fine_tune_model_result["success"]:
            raise Exception(f"{chat_by_fine_tune_model_result['message']}")

        return {
            "success": True,
            "message": "success to chat by fine tune",
            "data": {
                "fineTuneModel": body.fineTuneModel,
                "prompt": body.prompt,
                "botMessage": chat_by_fine_tune_model_result["data"]
            }
        }

    except Exception as e:
        print(e)
        logger.error(e)
        return {"success": False, "message": f"fail to chat by fine tune: {e}", "data": None}


@router.post("/paint", response_model=ApiResponse)
async def create_paint(paint: CreatePaintDTO):
    """
    ChatGPT3.5 활용하여 선택한 화가의 스타일로 그림 만들어주기
    """
    translate_description_result = translate_description(paint.description)

    if translate_description_result.success:
        prompt = f"{translate_description_result.data}, depicted in the style of {paint.author}'s paintings."
        generate_image_result = generate_image(prompt)
        if generate_image_result.success:
            return {
                "success": True,
                "message": "success to create paint",
                "data": generate_image_result.data
            }
        else:
            return {
                "success": False,
                "message": generate_image_result.message,
                "data": None
            }
    else:
        return {
            "success": False,
            "message": translate_description_result.message,
            "data": None
        }


@router.delete('/delete-fine-tune', response_model=ApiResponse)
async def delete_fine_tune(fineTuneModel: str = Form(...)):
    """
    파인 튜닝 모델 삭제하기
    """
    try:
        delete_fine_tune_model_result = delete_fine_tune_model(fineTuneModel)

        if not delete_fine_tune_model_result["success"]:
            raise Exception(f"{delete_fine_tune_model_result['message']}")

        return {
            "success": True,
            "message": "success to delete fine tune",
            "data": delete_fine_tune_model_result["data"]
        }

    except Exception as e:
        print(e)
        logger.error(e)
        return {"success": False, "message": f"fail to delete fine tune: {e}", "data": None}
