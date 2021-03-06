# End to End Batch ETL Pipelines

Project ini menggunakan beberapa referensi `image` atau `container` berikut:

* `postgres`: Postgres database menyimpan metadata Airflow & sebagai OLTP database.
    * Image: postgres:13.2
    * Database Port: 5432
    * References: https://hub.docker.com/_/postgres

* `airflow-webserver`: Airflow webserver and Scheduler ETL jobs.
    * Image: Dockerfile
    * Port: 8080
    * References: https://github.com/puckel/docker-airflow 

* `spark`: Spark Master.
    * Image: docker.io/bitnami/spark:3
    * Port: 8181
    * References: 
        * https://hub.docker.com/r/bitnami/spark 
        * https://github.com/bitnami/bitnami-docker-spark

* `spark-worker-N`: Spark Workers. Anda bisa menambahkan spark-worker di docker-compose file.
    * Image: docker.io/bitnami/spark:3
    * References: 
        * https://hub.docker.com/r/bitnami/spark 
        * https://github.com/bitnami/bitnami-docker-spark

* `hadoop`: Hadoop sebagai Data Lake & Data Warehouse.
    * Image: 
        * `docker-compose.yml`: teivah/hadoop:2.9.2
        * `docker-compose.yaml`: bde2020/hadoop
    * Port: 50070
    * References: 
        * https://hub.docker.com/r/teivah/hadoop
        * https://github.com/big-data-europe/docker-hadoop


### .
## Architecture Components

![](./images/architecture.png "Big Data Architecture")


### .
## Requirements

- *Docker*
- *Docker Compose*
- *Git (optional)*


### .
## Setup

### Clone project

Jika Anda `Windows User` maka atur configurasi git agar menggunakan Unix-style dengan command:
    
    $ git config --global core.autocrlf false

Clone repository ini dengan command:

    $ git clone https://github.com/arinannp/big-data-architecture.git

Make sure untuk jalankan command berikut bagi `Mac-os User` dan `Linux User`:

    $ sudo chmod 755 airflow/entrypoint.sh


### Build image dependencies

Pindah ke working direktori */big-data-architecture*

```Ada 2 docker-compose file untuk build & pull images, Anda bisa memilih salah satu```
    
- Jika menggunakan `docker-compose.yaml` dengan image bde2020/hadoop, jalankan command:
        
        $ docker-compose -f docker-compose.yaml build

- Jika menggunakan `docker-compose.yml` dengan image teivah/hadoop:2.9.2, jalankan command:
        
        $ docker-compose -f docker-compose.yml build


### Start containers

Untuk running containers, Anda bisa jalankan command berikut

- Jika Anda build images dengan file `docker-compose.yaml`, jalankan command:
        
        $ docker-compose -f docker-compose.yaml up -d

- Jika Anda build images dengan file `docker-compose.yml`, jalankan command:
        
        $ docker-compose -f docker-compose.yml up -d

Note: command -d digunakan agar running di background.


### Check containers logs

Anda bisa cek logs dari containers yang sudah di build, apakah containers/apps tersebut sudah ready

- Jika Anda build containers dengan file `docker-compose.yaml`, jalankan command:
        
        $ docker-compose -f docker-compose.yaml logs --tail 10

- Jika Anda build containers dengan file `docker-compose.yml`, jalankan command:
        
        $ docker-compose -f docker-compose.yml logs --tail 10

Note: command --tail 10 hanya menampilkan 10 logs terakhir.


### Access the containers or apps that were built

Airflow: http://localhost:8080

Postgres - Database Airflow:
* Server: localhost:5432
* Database: airflow
* User: airflow
* Password: airflow

Spark Master: http://localhost:8181

Hadoop Namenode: http://localhost:50070

Postgres - Database Transactional (OLTP) [source](https://www.kaggle.com/usdot/flight-delays?select=flights.csv):
* Server: localhost:5431
* Database: digitalskola
* User: digitalskola
* Password: digitalskola


### .
## How to Run an End to End Pipeline

1. Setting pepipost smtp credential *smtp_user* dan *smtp_password* di file [airflow/airflow.cfg](https://github.com/arinannp/big-data-architecture/blob/main/airflow/airflow.cfg) (jika belum punya account bisa mendaftar di https://www.pepipost.com/)
    ![](./images/smtp_host.png "SMTP Credential")

2. Jika Anda sudah mendaftarkan/verifikasi email sebagai subscription di https://www.pepipost.com/, Anda bisa merubah task dag send_email melalui file [dags/etl_flow_dag.py](https://github.com/arinannp/big-data-architecture/blob/main/dags/etl_flow_dag.py)
    ![](./images/send_mail.png "Mail Subs")

3. Konfigurasi spark-connection melalui Airflow UI http://localhost:8080, *klik Admin -> Connections*
    ![](./images/airflow_connections_menu.png "Airflow Connections")

4. Cari `spark_default` connection dan *klik Edit*
    ![](./images/airflow_spark_connection.png "Airflow Spark Connection")

5. Lakukan konfigurasi seperti gambar (Host spark://spark, Port 7077), dan *klik Save*:
    ![](./images/airflow_spark_config.png "Airflow Spark Connection")

6. Run Airflow DAG end_to_end_pipeline 
    ![](./images/run_airflow_dag.png "Run Airflow DAG")
   
7. Check Airflow DAG tree view
    ![](./images/airflow_dag_tree.png "Airflow Tree View")

8. Check Spark task id logs 
    ![](./images/airflow_dag_spark_logs.png "Airflow Spark Job Logs")

9. Check apakah data sudah tersimpan di Hadoop HDFS UI http://localhost:50070
    ![](./images/output_spark_job.png "HDFS Browse Directory")


### .
## How to run the Spark Apps via spark-submit
Anda juga bisa menjalankan Spark Jobs secara manual melalui CLI, dengan command:
```
$ docker exec -it spark spark-submit --master spark://spark:7077 --driver-class-path /usr/local/spark/connectors/postgresql-9.4.1207.jar --jars /usr/local/spark/connectors/postgresql-9.4.1207.jar /usr/local/spark/pipeline/etl_process.py
```

Test Code From datasets/*csv to Hadoop HDFS
```
$ docker exec -it spark spark-submit --master spark://spark:7077 /usr/local/spark/pipeline/etl_test.py
```

### .
## Data Modeling Datawarehouse
Source data schema dari Postgres OLTP [2015 Flight Delays and Cancellations](https://www.kaggle.com/usdot/flight-delays?select=flights.csv).

Data Warehouse Modeling menggunakan *combine* konsep dari [Ralph Kimball & Bill Inmon](https://www.astera.com/type/blog/data-warehouse-concepts/).

![](./images/erd.png "Schema Fact Table")


- Fact Table (denormalize table flights dan airlines).

    ![](./images/fact_table.png "Schema Fact Table")

- Dimensional Table (table airports).

    ![](./images/dims_table.png "Schema Dims Table")

- Data Warehouses HDFS path.

    ![](./images/hdfs_path.png "HDFS Path")


### .
## Source Code
- Main ETL spark code: [pipeline/etl_process.py](https://github.com/arinannp/big-data-architecture/blob/main/pipeline/etl_process.py)
- Source data validations code: [dags/validations/source_validation.py](https://github.com/arinannp/big-data-architecture/blob/main/dags/validations/source_validation.py)
- Result data validation code: [dags/validations/result_validation.py](https://github.com/arinannp/big-data-architecture/blob/main/dags/validations/result_validation.py)
- DAG code file: [dags/etl_flow_dag.py](https://github.com/arinannp/big-data-architecture/blob/main/dags/etl_flow_dag.py)


### .
## Stops and Removes Containers, Networks & Volumes
Anda bisa menghapus container hasil dari `docker-compose up` dengan command berikut

- Jika Anda build containers dengan file `docker-compose.yaml`, jalankan command:
        
        $ docker-compose -f docker-compose.yaml down

- Jika Anda build containers dengan file `docker-compose.yml`, jalankan command:
        
        $ docker-compose -f docker-compose.yml down


### .
## References
* https://github.com/cordon-thiago/airflow-spark
* https://github.com/big-data-europe/docker-hadoop
* https://github.com/puckel/docker-airflow 
