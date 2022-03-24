import logging
import os
import paramiko
import airflow_client.client
from pprint import pprint
from typing import List
from dynaconf import settings
from fastapi import FastAPI
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base
from airflow_client.client.api import dag_run_api
from airflow_client.client.model.error import Error


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

# # https://docs.sqlalchemy.org/en/14/orm/tutorial.html#connecting
Base = declarative_base()

# Airflow Configuration
# https://airflow.apache.org/docs/apache-airflow/stable/stable-rest-api-ref.html
# https://github.com/apache/airflow-client-python
configuration = airflow_client.client.Configuration(
    host=settings.get("airflow.url"),
    username=settings.get("airflow.username"),
    password=settings.get("airflow.password")
)


class FilePath(BaseModel):
    path: str


class Request(BaseModel):
    name: str
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
    logging.info("this is debug logging")
    return {"message": "Hello World"}


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