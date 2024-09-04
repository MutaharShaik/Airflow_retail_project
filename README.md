# Airflow_retail_project
Airflow retail project using pipeline with BigQuery, dbt, Soda
Overview
========

Welcome to Astronomer! This project was generated after you ran 'astro dev init' using the Astronomer CLI. This readme describes the contents of the project, as well as how to run Apache Airflow on your local machine.

Project Contents
================

Your Astro project contains the following files and folders:

- dags: This folder contains the Python files for your Airflow DAGs. By default, this directory includes one example DAG:
    - `example_astronauts`: This DAG shows a simple ETL pipeline example that queries the list of astronauts currently in space from the Open Notify API and prints a statement for each astronaut. The DAG uses the TaskFlow API to define tasks in Python, and dynamic task mapping to dynamically print a statement for each astronaut. For more on how this DAG works, see our [Getting started tutorial](https://docs.astronomer.io/learn/get-started-with-airflow).
- Dockerfile: This file contains a versioned Astro Runtime Docker image that provides a differentiated Airflow experience. If you want to execute other commands or overrides at runtime, specify them here.
- include: This folder contains any additional files( non- data pipelines)  that you want to include as part of your project. It is empty by default.
- packages.txt: Install OS-level packages needed for your project by adding them to this file. It is empty by default.
- requirements.txt: Install Python packages needed for your project by adding them to this file. It is empty by default.
- plugins: Add customized my airflow instance or community plugins for your project to this file. It is empty by default.
- airflow_settings.yaml: Use this local-only file to specify Airflow Connections, Variables, and Pools instead of entering them in the Airflow UI as you develop DAGs in this project.
-tests - to put some tests for the tasks
- .env - to export the environmental variables
Deploy Your Project Locally
- airflow_settings - to persist connections, pools and variables
===========================

1. Start Airflow on your local machine by running 'astro dev start'.

This command will spin up 4 Docker containers on your machine, each for a different Airflow component:

- Postgres: Airflow's Metadata Database
- Webserver: The Airflow component responsible for rendering the Airflow UI
- Scheduler: The Airflow component responsible for monitoring and triggering tasks
- Triggerer: The Airflow component responsible for triggering deferred tasks

2. Verify that all 4 Docker containers were created by running 'docker ps'.

Note: Running 'astro dev start' will start your project with the Airflow Webserver exposed at port 8080 and Postgres exposed at port 5432. If you already have either of those ports allocated, you can either [stop your existing Docker containers or change the port](https://docs.astronomer.io/astro/test-and-troubleshoot-locally#ports-are-not-available).

3. Access the Airflow UI for your local Airflow project. To do so, go to http://localhost:8080/ and log in with 'admin' for both your Username and Password.

You should also be able to access your Postgres Database at 'localhost:5432/postgres'.






Deploy Your Project to Astronomer
=================================

If you have an Astronomer account, pushing code to a Deployment on Astronomer is simple. For deploying instructions, refer to Astronomer documentation: https://docs.astronomer.io/cloud/deploy-code/

Contact
=======

The Astronomer CLI is maintained with love by the Astronomer team. To report a bug or suggest a change, reach out to our support.




## Project Description:
1. uploaded raw data in to GCS bucket 
2. With the data piepline we ingest the raw data from GCS to the BigQuery table that automatically created using Astro SDK and load file operator.
3. Implemented data Quality Checks using soda and external python operator (it allows to run in py venv to avoid conflicts)
4. created dbt models to generate the fact and dim tables using cosmos (best way to intercat dbt with airflow)
5. data Quality checks for the transfrom data 
6. create dbt models to generate metrics from the transform data from dim and fact tables 
7. data quality checks to make sure the metrics are correct
8. create the dashboard to show the data 

resources:
Data Engineer Project: An end-to-end Airflow data pipeline with BigQuery, dbt Soda, and more!
Data with Marc
https://registry.astronomer.io/providers/apache-airflow-providers-google/versions/10.14.0/modules/LocalFilesystemToGCSOperator

https://astro-sdk-python.readthedocs.io/en/stable/astro/sql/operators/load_file.html

https://docs.soda.io/soda-cl/soda-cl-overview.html

https://astronomer.github.io/astronomer-cosmos/

https://www.youtube.com/watch?v=DzxtCxi4YaA&t=2562s
