import os
from airflow.models import DAG
from airflow.utils.dates import days_ago
from airflow.operators.email_operator import EmailOperator
from airflow.operators.bash_operator import BashOperator
from airflow.operators.dummy_operator import DummyOperator
from airflow.contrib.operators.spark_submit_operator import SparkSubmitOperator
from datetime import timedelta



project_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dags")

args = {
    'owner': 'Airflow',
    'depends_on_past': False,
    'email': ['arinannp@gmail.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=1)
}

dag = DAG(
    dag_id="end_to_end_pipeline",
    default_args=args,
    description="pipeline etl from postgres to hadoop hdfs",
    schedule_interval="30 19 * * *",
    start_date=days_ago(2),
    tags=['pipelining']
)


start = DummyOperator(
    task_id='start',
    dag=dag
)

source_validate = BashOperator(
    task_id='source_data_validation',
    bash_command=f'python {project_dir}/validations/source_validation.py',
    dag=dag
)

result_validate = BashOperator(
    task_id='result_data_validation',
    bash_command=f'python {project_dir}/validations/result_validation.py',
    dag=dag
)

spark_job = SparkSubmitOperator(
    task_id="spark_job",
    application="/usr/local/spark/pipeline/etl_process.py",
    name="Batch ETL with Spark",
    conn_id="spark_default",
    verbose=1,
    conf={"spark.master":"spark://spark:7077"},
    jars="/usr/local/spark/connectors/postgresql-9.4.1207.jar",
    driver_class_path="/usr/local/spark/connectors/postgresql-9.4.1207.jar",
    dag=dag
)

send_email = EmailOperator(
    task_id='send_email',
    to='arinannp@gmail.com',
    subject='End to End Pipeline ETL Validation',
    html_content=
    """
        <p>Pipeline ETL Success Running</p> 
    """,
    dag=dag
)

end = DummyOperator(
    task_id='end',
    dag=dag
)

start >> source_validate >> spark_job >> result_validate >> send_email >> end