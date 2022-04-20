import logging
import os
import paramiko
import airflow_client.client
import shutil
import ntpath
import glob
import uvicorn
import requests

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

# https://realpython.com/python-logging/
logging.basicConfig(filename='app.log', filemode='w', format='[%(asctime)s] [%(levelname)s] - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

# Configuration Mode
mode = "development"
try:
    envMode = os.environ['MODE']
    mode = envMode
except KeyError:
    mode = "development"

print("Application Mode : {}".format(settings.get("mode")))

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

def createIfNotExists(path: str):
    isExist = os.path.exists(path)
    if not isExist:
        os.makedirs(path)
        logging.info(f"The working directory '{path}' is created")

def writeStringToFile(body: str, path: str):
    text_file = open(path, "w")
    text_file.write(body)
    text_file.close()
    logging.debug(f"Saved {path}.\n{body}")

working_directory = settings.get("working-path")
createIfNotExists(working_directory)

class FilePath(BaseModel):
    path: str

class Request(BaseModel):
    images: List[str]


class Response(BaseModel):
    job_id: Optional[str] = None
    success: Optional[str] = None
    message: Optional[str] = None


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
    logging.info("this is debug logging")
    return {"message": "Hello World"}


def runDag(job_id: str, json_path: str, json_file_path: str):
    _now = datetime.now()
    now = _now - timedelta(hours=9)
    date_time = now.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-4] + 'Z'

    airflow_server = settings.get("airflow.url")
    airflow_username = settings.get("airflow.username")
    airflow_password = settings.get("airflow.password")

    dag_name = "GWMS-PARTS"
    headers = {'accept': 'application/json', 'Content-Type': 'application/json'}
    auth = (airflow_username, airflow_password)
    body = {
        "conf": {
            "job_id": job_id,
            "base_path": json_path,
            "json_file_path": json_file_path
        },
        "dag_run_id": job_id,
        "logical_date": date_time
    }

    url = "{}/api/v1/dags/{}/dagRuns".format(airflow_server, dag_name)
    response = requests.post(url, headers=headers, auth=auth, data=json.dumps(body))
    response_body = response.content.decode("UTF-8")

    logging.info(f"Dag Run : {response_body}")

    return response


@app.post("/api/run/parts")
async def dagRunParts(body: Request):
    logging.info(f"{body}")

    yyyymmdd = datetime.now().strftime("%Y%m%d")
    job_id = datetime.now().strftime("%Y%m%d%H%M%S")

    json_path = "{}/{}/{}".format(working_directory, yyyymmdd, job_id)
    json_file_path = "{}/{}/{}/request.json".format(working_directory, yyyymmdd, job_id)
    createIfNotExists(json_path)
    writeStringToFile(','.join(body.images), json_file_path)

    logging.info(f"Airflow의 parts를 실행합니다.")

    runDag(job_id, json_path, json_file_path)

    response = Response()
    response.job_id = job_id
    response.success = "true"
    return response


@app.post("/api/run/{dagName}")
async def dagRun(request: Request):
    logging.info(f"Airflow의 {request.name}를 실행합니다.")
    return {"message": f"Hello {request.name}"}


@app.get("/api/info/{dagName}")
async def infoDag(dagName: str):
    logging.info(f"Airflow의 {dagName}의 정보를 확인합니다.")
    return {"message": f"Hello {dagName}"}


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
    logging.info("지정한 경로 {}의 모든 파일을 삭제합니다.".format(path))
    files = glob.glob("{}/*".format(path))
    for f in files:
        try:
            os.remove(f)
        except OSError as e:
            logging.warning("파일을 삭제할 수 없습니다. 파일명 : %s / 에러 : %s" % (f, e.strerror))

def copy_file(source_base_path: str, source_filename: str, target_base_path: str):
    head, tail = ntpath.split(source_filename)
    source_path = "{}/{}".format(source_base_path, source_filename)
    target_path = "{}/{}".format(target_base_path, tail)

    logging.info("소스파일 {}을 {} 파일로 복사합니다.".format(source_path, target_path))

    shutil.copyfile(source_path, target_path)

    logging.info("파일을 복사하였습니다.")


def copy_files(source_base_path: str, source_filenames: List[str], target_base_path: str):
    logging.info("소스 디렉토리 {}의 파일을 목적 디렉토리의 {}으로 복사를 시작합니다.".format(source_base_path, target_base_path))
    for filename in source_filenames:
        copy_file(source_base_path, filename, target_base_path)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(settings.get("port")))