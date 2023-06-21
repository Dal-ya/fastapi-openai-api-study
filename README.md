# OpenAI GPT관련 API 사용하기

- OpenAI 사의 GPT 관련 API를 사용하여 간단한 서비스를 만들어 본다.
  - https://platform.openai.com/docs/introduction
- 임베딩은 godly의 API를 사용한다.
  - https://godly.ai

## 요구사항

```shell
python 3.11.1
pipenv

# mac
brew install pipenv

# window, linux
pip install pipenv
```

## 설치 & 실행

```shell
# 가상환경 설정
pipenv --python 3.11.1
pipenv shell

# 설치
pipenv install

# 서버 실행
pipenv run start
```

## 몽고DB 로컬 설치(테스트용)

```shell
docker-compose up -d
```

## 배포
```shell
# 배포시 Pipfile 확인 사항
# --host 0.0.0.0 으로 설정 되어 있는 지 확인 후 배포
...
[scripts]
start = "uvicorn src.app:app --host 0.0.0.0 --port 8000 --reload"
...

```