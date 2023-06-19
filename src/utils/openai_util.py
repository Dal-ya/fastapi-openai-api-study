import mimetypes
import os
from pathlib import Path
import uuid
import openai
from fastapi import HTTPException, UploadFile
from dotenv import load_dotenv
from typing import Generic, TypeVar
from pydantic import BaseModel

load_dotenv()
openai.api_key = os.environ['OPENAI_API_KEY']

T = TypeVar("T")


class ResponseResult(BaseModel, Generic[T]):
    success: bool
    message: str
    data: T


class ResponseImage(BaseModel):
    url: str


async def fine_tune_save_file(file: UploadFile):
    try:
        # 파일 확장자 확인
        if not mimetypes.guess_type(file.filename)[0].startswith("text/"):
            raise HTTPException(status_code=400, detail="올바른 텍스트 파일을 업로드 해야 합니다.")

        # 파일 저장 폴더 생성
        UPLOAD_DIR = Path.cwd() / 'src' / 'fine-tune'
        UPLOAD_DIR.mkdir(exist_ok=True)

        # 파일 읽고 폴더에 저장
        file_content = await file.read()
        file_name_without_ext, _ = os.path.splitext(file.filename)
        file_name = f"{file_name_without_ext}-{str(uuid.uuid4())}.txt"

        with open(os.path.join(UPLOAD_DIR, file_name), "wb") as fp:
            fp.write(file_content)

        return {
            "success": True,
            "message": "success to save file",
            "data": {
                "fileName": file_name,
                "filePath": os.path.join(UPLOAD_DIR, file_name)
            }
        }

    except Exception as e:
        print(e)
        return {"success": False, "message": f"fail to save file, {e}", "data": {}}


def get_gpt3_responses(chunk: str, QUESTION_COUNT=5, TEMPERATURE_VALUE=0.5):
    # Create chat message with the request for the assistant
    messages = [{
        "role":
            "system",
        "content":
            "You are an assistant that generates JSONL prompts and completions based on input parts from a novel for "
            "fine tuning."
    }, {
        "role":
            "user",
        "content":
            f"다음의 <> 안에 오는 내용에 대한 직접적인 질문과 그 질문에 대한 답변의 쌍 {QUESTION_COUNT}개를 한국어로 생성하여 그 결과만 반드시 {{\"prompt\": "
            f"\"질문\",\"completion\": \"답변\"}}의 jsonl 포맷으로 출력해. each line의 마지막, 즉 }} 문자 다음에는 개행문자를 반드시 추가해. jsonl 포맷 "
            f"데이터 이외의 내용은 절대 출력하면 안돼. 모든 Question의 처음 부분에 [황순원 소설 소나기]라는 문구를 꼭 추가해. 질문과 답변을 만들때 반드시 <> 내의 내용만 한정해서 "
            f"사용하고 없는 내용을 상상해서 지어내면 안돼. 확실히 알수 없는 답변이 있으면 내용을 절대 상상하지 말고 해당 질문 답변 쌍을 출력에서 제외해. 질문시에 용어에 대한 질문과 등장인물에게 "
            f"물어보는 질문은 절대 하면 안돼. <{chunk}>"
    }]

    # Generate response from OpenAI's gpt-3.5-turbo

    try:
        print(
            f"openai.ChatCompletion API is being called to create {QUESTION_COUNT} Q&A pairs"
        )
        response = openai.ChatCompletion.create(model="gpt-3.5-turbo",
                                                messages=messages,
                                                temperature=TEMPERATURE_VALUE)

        if response['choices'][0]['finish_reason'] == "stop":  # 성공
            print("The API Request has completed, Finish Reason: stop")

            # Extract assistant's reply
            return response['choices'][0]['message']['content']
        else:  # 실패
            print(
                f"The API request has not stopped, Finish Reason: {response['choices'][0]['finish_reason']}"
            )
            return None

    except openai.error.APIError as e:  # 에러
        print(f"The API request has failed, Error: {e}")
        return None


def create_jsonl(file_name: str, file_path: str, CHUNK_SIZE=500):
    try:
        with open(file_path, "r", encoding="UTF-8") as input_file:
            data = input_file.read()

        # Replace newline characters with space and replace quotes with apostrophes
        data = data.replace('\n', ' ').replace('"', "'")

        chunks = [data[i:i + CHUNK_SIZE] for i in range(0, len(data), CHUNK_SIZE)]

        # 파일 저장 폴더 생성
        JSONL_DIR = Path.cwd() / 'src' / 'jsonl-files'
        JSONL_DIR.mkdir(exist_ok=True)

        file_name_without_ext, _ = os.path.splitext(file_name)
        jsonl_file_name = f"{file_name_without_ext}-{str(uuid.uuid4())}.jsonl"

        with open(os.path.join(JSONL_DIR, jsonl_file_name), "w", encoding="UTF-8") as output_file:
            for chunk in chunks:
                response: str = get_gpt3_responses(chunk)
                if response is None:
                    raise Exception("The get_gpt3_responses has failed")

                # Write response directly to output.jsonl
                output_file.write(response + "\n")

        return {"success": True, "message": "success to create jsonl file", "data": {
            "fileName": jsonl_file_name,
            "filePath": os.path.join(JSONL_DIR, jsonl_file_name)
        }}
    except Exception as e:
        print(f"Error: {e}")
        return {"success": False, "message": f"fail to create jsonl file, {e}", "data": {}}


def translate_description(description: str) -> ResponseResult[str | dict]:
    try:
        messages = [
            {"role": "system", "content": "You are a very helpful assistant that translates English to Korean."},
            {
                "role": "user",
                "content": f"'{description}'. 문장을 영어로 번역해 줘."
            }
        ]

        response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages, temperature=0)

        if response['choices'][0]['finish_reason'] == "stop":
            return ResponseResult(**{
                "success": True,
                "message": "success to translate",
                "data": response["choices"][0]["message"]["content"]
            })
        else:
            return ResponseResult(**{
                "success": False,
                "message": f"Request has not stopped. Finish Reason: {response['choices'][0]['finish_reason']}",
                "data": None
            })
    except openai.error.APIError as e:
        return ResponseResult(**{
            "success": False,
            "message": f"Request has failed, {e}",
            "data": None
        })


def generate_image(prompt: str) -> ResponseResult[list[ResponseImage] | dict]:
    print("prompt: ", prompt)
    try:
        response = openai.Image.create(
            prompt=prompt,
            n=1,
            size="512x512",
        )

        return ResponseResult(**{
            "success": True,
            "message": "success to generate image",
            "data": response["data"]
        })
    except openai.error.APIError as e:
        return ResponseResult(**{
            "success": False,
            "message": f"Request has failed, {e}",
            "data": None
        })


def upload_jsonl(file_path: str, purpose="fine-tune"):
    try:
        with open(file_path, "rb") as f:
            print("file_path: ", file_path)
            response = openai.File.create(file=f, purpose=purpose)
            print("response: ", response)
            print("response type", type(response))
            return {
                "success": True,
                "message": "success to upload jsonl",
                "data": {"fileId": response["id"]}
            }
    except openai.error.APIError as e:
        print(e)
        return {
            "success": False,
            "message": f"fail upload jsonl, {e}",
            "data": None
        }


def get_file_list():
    try:
        response = openai.File.list()
        return {
            "success": True,
            "message": "success to get file list",
            "data": response["data"]
        }
    except openai.error.APIError as e:
        print(e)
        return {
            "success": False,
            "message": f"fail to get file list, {e}",
            "data": None
        }


def create_fine_tune_model(openai_file_id: str, model_name="test-fine-tune"):
    try:
        response = openai.FineTune.create(
            training_file=openai_file_id,
            model="curie",  # "ada", "babbage", "curie(default)", "davinci"
            suffix=model_name
            # n_epochs=1, # default: 4
            # batch_size=1, # default: null
        )
        return {
            "success": True,
            "message": "success to create fine tune",
            "data": response["id"]  # "ft-AF1WoRqd3aJAHsqc9NY7iL8F"
        }

    except openai.error.APIError as e:
        print(e)
        return {
            "success": False,
            "message": f"fail to create fine tune, {e}",
            "data": None
        }


def get_fine_tune_list():
    try:
        response = openai.FineTune.list()
        return {
            "success": True,
            "message": "success to get fine tune list",
            "data": response["data"]
        }
    except openai.error.APIError as e:
        print(e)
        return {
            "success": False,
            "message": f"fail to get fine tune list, {e}",
            "data": None
        }


def delete_fine_tune_model(fine_tune_model: str):
    try:
        response = openai.Model.delete(fine_tune_model)
        return {
            "success": True,
            "message": "success to delete fine tune",
            "data": response
        }
    except openai.error.APIError as e:
        print(e)
        return {
            "success": False,
            "message": f"fail to delete fine tune, {e}",
            "data": None
        }


def chat_by_fine_tune_model(fine_tune_model: str, prompt: str):
    try:
        response = openai.Completion.create(
            engine=fine_tune_model,  # Fine-tuned model
            prompt=prompt,
            temperature=0.8,
            max_tokens=200
        )

        return {
            "success": True,
            "message": "success to chat by fine tune",
            "data": response["choices"][0]["text"]
        }

    except openai.error.APIError as e:
        print(e)
        return {
            "success": False,
            "message": f"fail to chat by fine tune: {e}",
            "data": None
        }
