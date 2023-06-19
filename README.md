# OpenAI GPT관련 API 사용하기

- OpenAI 사의 GPT 관련 API를 사용하여 간단한 서비스를 만들어 본다.
- https://platform.openai.com/docs/introduction

## 요구사항

```shell
python ^3.11
pipenv
```

## 설치 & 실행

```shell
# 가상환경 설정
pipenv --python 3.11
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