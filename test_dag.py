from datetime import datetime
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.bash import BashOperator

default_args = {
    'start_date': datetime(2022, 3, 1),
    'email': ['airflow_notification@thisisadummydomain.com'],
    'email_on_failure': False
}

dag = DAG('hello_world',
          description='Hello world DAG',
          default_args=default_args,
          schedule_interval= "@once"
          )

def print_hello():
    print('Hello world :)')

with dag:
    python_task = PythonOperator(task_id='hello_task_id', python_callable=print_hello)

    python_task