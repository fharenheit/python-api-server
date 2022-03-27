import time
import airflow_client.client

from airflow_client.client.api import dag_run_api
from airflow_client.client.model.error import Error
from pprint import pprint
from airflow_client.client.model.dag_state import DagState
from datetime import datetime

configuration = airflow_client.client.Configuration(
    host = "http://localhost:8080/api/v1",
    username = 'admin',
    password = 'admin'
)

now = datetime.now()
print(now)

date_time = now.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-4] + 'Z'
print(date_time)

with airflow_client.client.ApiClient(configuration) as api_client:
    api_instance = dag_run_api.DAGRunApi(api_client)
    dag_id = 'hello_world'
    dag_run = dag_run_api.DAGRun(
        dag_run_id = "hello_task_id",
        logical_date = now,
        execution_date = now,
        state = DagState("queued"),
        conf = {},
    )

    try:
        api_response = api_instance.post_dag_run(dag_id, dag_run)
        pprint(api_response)
    except airflow_client.client.ApiException as e:
        print("Exception when calling DAGRunApi->post_dag_run: %s\n" % e)