from datetime import datetime, timedelta
from platform import python_version
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator
from airflow.operators.python_operator import PythonVirtualenvOperator
from airflow.operators.bash import BashOperator

current = datetime.combine(datetime.today() - timedelta(0), datetime.min.time())

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': current,
    'email': ['airflow_notification@thisisadummydomain.com'],
    'email_on_failure': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

dag = DAG('hello_world',
          description='Hello world DAG',
          default_args=default_args,
          schedule_interval=None
          )


def print_hello(**kwargs):
    print(kwargs['dag_run'].conf.get('image_path'))
    print('Hello world :)')


command = """
    /Users/fharenheit/airflow/dags/venv/bin/python /Users/fharenheit/airflow/dags/hello.py
    """
command1 = """
    /Users/fharenheit/airflow/dags/venv/bin/python /Users/fharenheit/airflow/dags/hello.py {{ dag_run.conf }}
    """

with dag:
    bash_task = BashOperator(
        task_id='bash_test',
        bash_command=command,
        params={},
        dag=dag,
    )

    bash_task
