# retail.py

from airflow.decorators import dag, task
#  decorators are Task API's instead of using WITH instance in the dag we use alternative "dag" decorator to instantiate the DAG object
from datetime import datetime

from airflow.providers.google.cloud.transfers.local_to_gcs import LocalFilesystemToGCSOperator
from airflow.providers.google.cloud.operators.bigquery import BigQueryCreateEmptyDatasetOperator

from astro import sql as aql
from astro.files import File   # used for input file parameter
from astro.sql.table import Table, Metadata    # used for output table parameter
from astro.constants import FileType      # to indicate file we use is a CSV file
from airflow.models.baseoperator import chain    # to create the dependencies
# transform task imports
from include.dbt.cosmos_config import DBT_PROJECT_CONFIG, DBT_CONFIG
from cosmos.airflow.task_group import DbtTaskGroup
from cosmos.constants import LoadMode
from cosmos.config import ProjectConfig, RenderConfig

@dag(
    start_date=datetime(2023, 1, 1),
    schedule=None,         # as we want to trigger DAG manually
    catchup=False,
    tags=['retail'],          # useful to categorize and filter the data pipeline in Airflow UI
)
def retail():       # define the function "retail" which will be the Unique identifier of the data pipeline
# now we want to ingest the data in to GCS bucket we created
# to know which operator gco  go to https://registry.astronomer.io/providers/apache-airflow-providers-google/versions/10.14.0/modules/LocalFilesystemToGCSOperator

# task 1:
    upload_csv_to_gcs = LocalFilesystemToGCSOperator(
        task_id='upload_csv_to_gcs',
        src='include/dataset/online_retail.csv',
        dst='raw/online_retail.csv',
        bucket='mutahar_online_retail',          # created on GCP
        gcp_conn_id='gcp',
        mime_type='text/csv',        # mime_type stands for "Multipurpose Internet Mail Extensions type" and is a standard way to indicate the nature and format of a file
    )

retail()

# best practice is to test the tasks when ever we added the tasks to the data pipeline
#
# (venv) (base) mohammedmutaharshaik@Mohammeds-MacBook-Pro Airflow_RetailProject  % astro dev bash
# Execing into the scheduler container
#
# astro@d40b1b6fb365:/usr/local/airflow$ airflow tasks test retail upload_csv_to_gcs 2023-01-01

#airflow.exceptions.AirflowNotFoundException: The conn_id `gcp` isn't defined
# check the connection is saved on Airflow for gcp
# check again till we get Marking tasks as success


# now go and check on GCS in buckets as it is successfully upload the online_retail.csv in to bucket.

# 2nd task: Now we want to load the csv file as a big Query table and for that we need to create a
#Create an empty Dataset (schema equivalent)


    create_retail_dataset = BigQueryCreateEmptyDatasetOperator(
        task_id='create_retail_dataset',
        dataset_id='retail',
        gcp_conn_id='gcp',
    )


# check the connection is saved on Airflow for gcp
# (venv) (base) mohammedmutaharshaik@Mohammeds-MacBook-Pro Airflow_RetailProject  % astro dev bash
# astro@d40b1b6fb365:/usr/local/airflow$ airflow tasks test retail create_retail_dataset 2023-01-01
# check till we get Marking tasks as success
## now go and check on google Big Query as it is successfully upload the schema retail in to Big Query.


# task 3: Create the task to load the CSV file into a BigQuery schema "retail" and in that "raw_invoices" table
# we can Use Astro SDK https://github.com/astronomer/astro-sdk

# Astro SDK allows to help in making rapid and clean development of Extract Load and transform, workflows using python and SQL
# https://astro-sdk-python.readthedocs.io/en/stable/
#we get lot of operators which helps to manage the operations between the databases and files like (load_file operator
# https://astro-sdk-python.readthedocs.io/en/stable/astro/sql/operators/load_file.html




    gcs_to_raw = aql.load_file(
        task_id='gcs_to_raw',
        input_file=File(
            'gs://mutahar_online_retail/raw/online_retail.csv',
            conn_id='gcp',
            filetype=FileType.CSV,
        ),
        output_table=Table(
            name='raw_invoices',
            conn_id='gcp',
            metadata=Metadata(schema='retail')
        ),
        use_native_support=False,      # another paramter
    )


# check the connection is saved on Airflow for Big Query
# (venv) (base) mohammedmutaharshaik@Mohammeds-MacBook-Pro Airflow_RetailProject  % astro dev bash
# astro@d40b1b6fb365:/usr/local/airflow$ airflow tasks test retail gcs_to_raw 2023-01-01
# check till we get Marking tasks as success
## now go and check on google Big Query as it is successfully upload the schema retail -(raw_invoices) in to Big Query.



# @task.external_python --> external_python decorator is correspondence to the external python operator
# that allows you to run the python code wth in the pre created python virtual environment.
# It helps to avoid the dependency conflict as this task is isloated from its environment

# task 4:
# Implement the data quality checks for the raw data
    @task.external_python(python='/usr/local/airflow/soda_venv/bin/python')     # running python using Soda venv
    def check_load(scan_name='check_load', checks_subpath='sources'):    # checks_subpath --> where the checks are
        from include.soda.check_function import check

        return check(scan_name, checks_subpath)
    # check_load()



# create  a new task transform which is a DbtTaskGroup that represents your dbt models in the task group
# where each model will be a task in that group --> below added on the top
# from include.dbt.cosmos_config import DBT_PROJECT_CONFIG, DBT_CONFIG
# from cosmos.airflow.task_group import DbtTaskGroup
# from cosmos.constants import LoadMode
# from cosmos.config import ProjectConfig, RenderConfig

# task 5:
    transform = DbtTaskGroup(
        group_id='transform',                 # we see in Airflow UI
        project_config=DBT_PROJECT_CONFIG,     # comes from cosmos_config file
        profile_config=DBT_CONFIG,
        render_config=RenderConfig(             # how to fetch those dbt models using render_config and expects 2 arguments
            load_method=LoadMode.DBT_LS,
            select=['path:models/transform']
        )
    )

# task 6: Transformation checks: using soda
# Implement the data quality checks for the transform data
    @task.external_python(python='/usr/local/airflow/soda_venv/bin/python')     # running python using Soda venv
    def check_transform(scan_name='check_transform', checks_subpath='transform'):    # checks_subpath --> where the checks are
        from include.soda.check_function import check

        return check(scan_name, checks_subpath)
    # check_transform()


# task 7: to create 3 tables that will correspond to metrics derived from the dimension and the fact tables derived from dbt
    report = DbtTaskGroup(
        group_id='report',
        project_config=DBT_PROJECT_CONFIG,
        profile_config=DBT_CONFIG,
        render_config=RenderConfig(
            load_method=LoadMode.DBT_LS,
            select=['path:models/report']
        )
    )

# task : 8
    @task.external_python(python='/usr/local/airflow/soda_venv/bin/python')
    def check_report(scan_name='check_report', checks_subpath='report'):
        from include.soda.check_function import check

        return check(scan_name, checks_subpath)
    # check_report()



    # creating dependencies using chain
    chain(
        upload_csv_to_gcs,
        create_retail_dataset,
        gcs_to_raw,
        check_load,
        transform,
        check_transform(),
        report,
        check_report()            # now remove the function calls of checks above
    )
retail()
