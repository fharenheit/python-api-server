from setuptools import setup, find_packages

setup(
    name='airflow-api-server',
    version='1.0.0',
    py_modules=['airflow-api-server'],
    install_requires=[
        'apache-airflow-client==2.2.0',
        'dynaconf==3.1.7',
        'fastapi==0.75.0',
        'paramiko==2.10.3',
        'pydantic==1.9.0',
        'requests==2.27.1',
        'SQLAlchemy==1.4.32',
        'python-gitlab==3.2.0',
        'GitPython==3.1.27'
    ],
    entry_points={
    })
