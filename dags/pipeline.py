from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta

import os
import random
import pandas as pd

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 12, 29),
    'email': ['rehand.gregor@gmail.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Define the DAG
dag = DAG(
    'data_pipeline',
    default_args=default_args,
    description='A pipeline to ingest JSON data on scientific papers and store it in PostgreSQL and Neo4j',
    schedule_interval=timedelta(days=1),
)
#Test data set of 150 random records
def ingest_data_test(**kwargs):
    df = pd.read_json('/opt/airflow/data/sampled_articles.json', lines=True)
    filepath = '/opt/airflow/data/ingested.json'
    df.to_json(filepath)
    return filepath


#Production workflow
def ingest_data_prod(**kwargs):
    partition_size = 50000
    number_of_partitions = 4
    all_data = number_of_partitions * partition_size
    data = []

    file_path = "./arxiv/arxiv-metadata-oai-snapshot.json"

    with open(file_path, 'r') as read_file:
        data = read_file.readlines()

    # Randomly sample 200K lines
    random_sample = random.sample(data, all_data)

    # Create a directory for partitions
    partitions_path = './arxiv/partitions'

    # Check whether directory already exists
    if not os.path.exists(partitions_path):
        os.mkdir(partitions_path)


    for i in range(number_of_partitions):
        # Select the first num_lines objects
        selected_data = random_sample[i * partition_size:(i + 1) * partition_size]

    # Open a new JSON file for writing
    with open(partitions_path + '/partition' + str(i) + '.json', 'w') as write_file:
        for line in selected_data:
            # Write the string to the file
            write_file.write(line)

    partition_path = partitions_path + "/partition1.json"

    # Read the data into pandas dataframe
    df = pd.read_json(partition_path, lines=True)
    return df

def clean_transform_data(**kwargs):
    df = pd.read_json('/opt/airflow/data/ingested.json')
    df.drop('abstract', axis=1)
    filepath = '/opt/airflow/data/transformed.json'
    df.to_json(filepath)


def enrich_data(**kwargs):
    df = pd.read_json('/opt/airflow/data/transformed.json')
    # null_doi = []
    # for record in df.iterrows():
    #     if pd.notnull(record['doi']):
    #         # query crossref
    #         print(record['doi'])
    #     else:
    #         null_doi.append(record)
    filepath = '/opt/airflow/data/enriched.json'
    df.to_json(filepath)

def load_to_neo4j(**kwargs):
    df = pd.read_json( '/opt/airflow/data/enriched.json')
    pass

def load_to_postgres(**kwargs):
    df = pd.read_json('/opt/airflow/data/enriched.json')
    from postgres.load_postgres_data import connect, load_data
    conn, cursor = connect()
    for record in df.to_dict('records'):
        load_data(cursor, record)
    cursor.close()
    conn.close()

ingest_task = PythonOperator(
    task_id='ingest',
    #python_callable=ingest_data_prod,
    python_callable=ingest_data_test,
    dag=dag,
)

clean_transform_task = PythonOperator(
    task_id='clean_transform',
    python_callable=clean_transform_data,
    dag=dag,
)

enrich_task = PythonOperator(
    task_id='enrich',
    python_callable=enrich_data,
    dag=dag,
)

load_to_neo4j_task = PythonOperator(
    task_id='load_to_neo4j',
    python_callable=load_to_neo4j,
    dag=dag,
)


load_to_postgres_task = PythonOperator(
    task_id='load_to_postgres',
    python_callable=load_to_postgres,
    dag=dag,
)

ingest_task >> clean_transform_task >> enrich_task >> [load_to_neo4j_task, load_to_postgres_task]
