# FastAPI 기반 Python API Server


## Install packages

패키지를 일괄 설치하기 위해서 다음의 커맨드를 실행합니다.

```
# pip install -r requirements.txt
```

설치한 패키지의 목록을 뽑아내기 위해서는 다음의 커맨드를 실행합니다.

```
# pip freeze > requirements.txt
```

## Development 

Virtual Environment를 다음과 같이 생성합니다.

```
# pip install virtualenv
# python3 -m venv venv
# source venv/bin/activate OR Source venv/Scripts/python.exe
```

개발을 위해서 `uvicorn`을 설치하고 실행합니다. `uvicorn`은 변경된 파일을 자동으로 감지하여 업데이트를 자동으로 합니다. 

```
# pip install uvicorn 
# uvicorn main:app --reload
```

## Wheel Packaging

```
# pip install wheel
# python setup.py bdist_wheel
```