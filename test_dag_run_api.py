import time
import random
import requests
import json
from datetime import datetime, timedelta

_now = datetime.now()
now =  _now - timedelta(hours=9)
print(now)

date_time = now.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-4] + 'Z'
job_id = "job_{}".format(_now.strftime('%Y%m%d%H%M%S'))
print(date_time)

# Airflow의 airflow.cfg 파일에서 다음을 추가하도록 함
# auth_backend = airflow.api.auth.backend.basic_auth

airflow_server = "http://localhost:8080"
airflow_username = "admin"
airflow_password = "admin"
 
dag_name = "hello_world"
headers = { 'accept': 'application/json', 'Content-Type': 'application/json'}
auth = (airflow_username, airflow_password)
body = {
  "conf": {
      "image_path": "/project_data/claim/part_images",
      "output_path": ""
  },
  "dag_run_id": job_id,
  "logical_date": date_time
}

url = "{}/api/v1/dags/{}/dagRuns".format(airflow_server, dag_name)
response = requests.post(url, headers=headers, auth=auth, data=json.dumps(body)) 
print(response.content.decode("UTF-8"))