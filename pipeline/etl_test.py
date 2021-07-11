import os
from pyspark.sql import SparkSession
from datetime import datetime



projectDir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print(projectDir)

spark = SparkSession \
    .builder \
    .config("spark.hadoop.dfs.client.use.datanode.hostname", "true") \
    .appName('Batch Pipeline ETL').getOrCreate()
    
spark.sparkContext.setLogLevel('WARN')


dfAirlines = spark.read.csv(os.path.join(projectDir, "datasets/airlines.csv"), header=True)
dfAirports = spark.read.csv(os.path.join(projectDir, "datasets/airports.csv"), header=True)
dfFlights = spark.read.csv(os.path.join(projectDir, "datasets/flights.csv"), header=True)
dfAirlines.show()
dfAirports.show()
dfFlights.show()


partitionDate = datetime.today().strftime("%Y%m%d")
dfAirlines.write.parquet(f"hdfs://hadoop:9000/Airlines_{partitionDate}", mode='overwrite')
dfAirports.write.parquet(f"hdfs://hadoop:9000/Airports_{partitionDate}", mode='overwrite')
dfFlights.write.parquet(f"hdfs://hadoop:9000/Flights_{partitionDate}", mode='overwrite')