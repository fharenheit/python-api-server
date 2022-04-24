import logging
import os
import paramiko
import airflow_client.client
import shutil
import ntpath
import glob
import requests
import json

from pprint import pprint
from typing import List, Optional
from dynaconf import settings
from fastapi import FastAPI
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base
from airflow_client.client.api import dag_run_api
from airflow_client.client.model.error import Error
from datetime import datetime, timedelta

from tinydb import TinyDB, Query
from tinydb.operations import delete, increment, decrement, add, subtract, set
from tinydb.table import Document

# Configuration Mode
mode = "development"
try:
    envMode = os.environ['MODE']
    mode = envMode
except KeyError:
    mode = "development"

def getLogger():
    logger = logging.getLogger(__name__)

    formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] - %(message)s')

    streamHandler = logging.StreamHandler()
    fileHandler = logging.handlers.RotatingFileHandler('test.log', maxBytes=1024 * 1024 * 10, backupCount=10)

    streamHandler.setFormatter(formatter)
    fileHandler.setFormatter(formatter)

    logger.addHandler(streamHandler)
    logger.addHandler(fileHandler)

    logger.setLevel(logging.DEBUG)

    return logger

logger = getLogger()

logger.info("Application Mode : {}".format(settings.get("mode")))

# https://fastapi.tiangolo.com/tutorial/body/
app = FastAPI()

# https://docs.sqlalchemy.org/en/14/orm/tutorial.html#connecting
Base = declarative_base()

# Airflow Configuration
# https://airflow.apache.org/docs/apache-airflow/stable/stable-rest-api-ref.html
# https://github.com/apache/airflow-client-python
configuration = airflow_client.client.Configuration(
    host=settings.get("airflow.url"),
    username=settings.get("airflow.username"),
    password=settings.get("airflow.password")
)

db = TinyDB(settings.get("database-path"))


class FilePath(BaseModel):
    path: Optional[str]


class Request(BaseModel):
    job_id: Optional[str]
    files: List[FilePath]


class Response(BaseModel):
    success: str
    message: str


class DagInfo(BaseModel):
    dagName: str
    status: str
    startTime: str
    endTime: str


class Log(Base):
    __tablename__ = 'logging'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    fullname = Column(String)
    nickname = Column(String)

    def __repr__(self):
        return "<User(name='%s', fullname='%s', nickname='%s')>" % (self.name, self.fullname, self.nickname)


@app.get("/")
async def root():
    logger.info("this is debug logging")
    return {"message": "Hello World"}


@app.post("/api/run/{dagName}")
async def dagRun(request: Request):
    logger(request)

    dag_name = "hello_world"
    headers = {'accept': 'application/json', 'Content-Type': 'application/json'}
    auth = ("admin", "admin")

    _now = datetime.now()
    now = _now - timedelta(hours=9)
    date_time = now.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-4] + 'Z'
    job_id = "job_{}".format(_now.strftime('%Y%m%d%H%M%S'))
    final_job_id = ""

    if request.job_id == None:
        final_job_id = job_id
    else:
        final_job_id = request.job_id

    image_paths = []
    for file in request.files:
        image_paths.append(file.path)

    body = {
        "conf": {
            "image_paths": ",".join(image_paths)
        },
        "dag_run_id": final_job_id,
        "logical_date": date_time
    }

    print(body)

    url = "{}/api/v1/dags/{}/dagRuns".format("http://localhost:8080", dag_name)
    response = requests.post(url, headers=headers, auth=auth, data=json.dumps(body)).json()
    return response

@app.get("/api/info/{dagName}/{jobId}")
async def dagInfo(dagName: str, jobId: str):
    logger.info(f"Dag Name : {dagName}")
    logger.info(f"Job ID : {jobId}")

    headers = {'accept': 'application/json', 'Content-Type': 'application/json'}
    auth = ("admin", "admin")

    url = "{}/api/v1/dags/{}/dagRuns/{}".format("http://localhost:8080", dagName, jobId)
    logger.info(url)
    response = requests.get(url, headers=headers, auth=auth).json()
    logger.info(response)

    return response


@app.get("/api/detail/{dagName}/{jobId}")
async def dagDetail(dagName: str, jobId : str):
    logger.info(f"Dag Name : {dagName}")
    logger.info(f"Job ID : {jobId}")

    headers = {'accept': 'application/json', 'Content-Type': 'application/json'}
    auth = ("admin", "admin")

    url = "{}/api/v1/dags/{}/dagRuns/{}/taskInstances/bash_test".format("http://localhost:8080", dagName, jobId)
    logger.info(url)
    response = requests.get(url, headers=headers, auth=auth).json()
    logger.info(response)

    return response


@app.get("/api/log/{dagName}/{jobId}/{tryNumber}")
async def dagLog(dagName: str, jobId : str, tryNumber: str):
    logger.info(f"Dag Name : {dagName}")
    logger.info(f"Job ID : {jobId}")

    headers = {'accept': 'application/json', 'Content-Type': 'application/json'}
    auth = ("admin", "admin")

    url = "{}/api/v1/dags/{}/dagRuns/{}/taskInstances/bash_test/logs/{}".format("http://localhost:8080", dagName, jobId, tryNumber)
    logger.info(url)
    response = requests.get(url, headers=headers, auth=auth).json()
    print(response)

    return response


def pullGitlab():
    server = settings.get("gitlab.server")
    username = settings.get("gitlab.username")
    password = settings.get("gitlab.password")
    cmd_to_execute = settings.get("gitlab.command")

    ssh = paramiko.SSHClient()
    ssh.connect(server, username=username, password=password)
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(cmd_to_execute)


# https://github.com/apache/airflow-client-python/blob/master/airflow_client/docs/DAGRunApi.md
def runDag(dagName: str):
    with airflow_client.client.ApiClient(configuration) as api_client:
        api_instance = dag_run_api.DAGRunApi(api_client)
        dag_id = "dag_id_example"
        dag_run_id = "dag_run_id_example"

        # example passing only required values which don't have defaults set
        try:
            # Delete a DAG run
            api_instance.delete_dag_run(dag_id, dag_run_id)
        except client.ApiException as e:
            print("Exception when calling DAGRunApi->delete_dag_run: %s\n" % e)


def delete_files(path: str):
    logger.info("지정한 경로 {}의 모든 파일을 삭제합니다.".format(path))
    files = glob.glob("{}/*".format(path))
    for f in files:
        try:
            os.remove(f)
        except OSError as e:
            logger.warning("파일을 삭제할 수 없습니다. 파일명 : %s / 에러 : %s" % (f, e.strerror))


def copy_file(source_base_path: str, source_filename: str, target_base_path: str):
    head, tail = ntpath.split(source_filename)
    source_path = "{}/{}".format(source_base_path, source_filename)
    target_path = "{}/{}".format(target_base_path, tail)

    logger.info("소스파일 {}을 {} 파일로 복사합니다.".format(source_path, target_path))

    shutil.copyfile(source_path, target_path)

    logger.info("파일을 복사하였습니다.")


def copy_files(source_base_path: str, source_filenames: List[str], target_base_path: str):
    logger.info("소스 디렉토리 {}의 파일을 목적 디렉토리의 {}으로 복사를 시작합니다.".format(source_base_path, target_base_path))
    for filename in source_filenames:
        copy_file(source_base_path, filename, target_base_path)

