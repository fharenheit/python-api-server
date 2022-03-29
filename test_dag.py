from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator

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
          schedule_interval= None
          )

def print_hello(**kwargs):
    print(kwargs['dag_run'].conf.get('image_path'))
    print('Hello world :)')

with dag:
    python_task = PythonOperator(task_id='hello_task_id', python_callable=print_hello, provide_context=True)

    python_task