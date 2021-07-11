import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, concat_ws, sum
from datetime import datetime



projectDir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

#Notes: .master("local[*]") bisa dihapus jika ingin berjalan di Spark Standalone Cluster (localhost:8181) spark://spark:7077
spark = SparkSession \
    .builder \
    .master("local[*]") \
    .config("spark.hadoop.dfs.client.use.datanode.hostname", "true") \
    .config('spark.driver.extraClassPath', os.path.join(projectDir, 'connectors/postgresql-9.4.1207.jar')) \
    .appName('Batch Pipeline ETL').getOrCreate()
    
spark.sparkContext.setLogLevel('WARN')



# Extract Data Flight Delays and Cancellations From PostgresDB
conn: str = "jdbc:postgresql://postgres-db:5432/digitalskola"
properties: dict = {
    "user": "digitalskola",
    "password": "digitalskola",
    "driver": "org.postgresql.Driver"
}

dfAirlines = spark.read.jdbc(conn, table="airlines",properties=properties)
dfAirports = spark.read.jdbc(conn, table="airports",properties=properties)
dfFlights = spark.read.jdbc(conn, table="flights",properties=properties)


# Transform Data Airlines Flight Delays and Cancellations
dateList = ["year", "month", "day"]
dfCleanedFlights = dfFlights \
            .withColumnRenamed("airline", "id_airline") \
            .fillna("No Cancellation", ["cancellation_reason"]) \
            .fillna(0, ["air_system_delay", "security_delay", "airline_delay", "late_aircraft_delay", "weather_delay"]) \
            .fillna("UNKNOWN", ["tail_number"]) \
            .withColumn("date", concat_ws("-", *dateList) \
            .cast("date"))

joinExpr = dfAirlines["iata_code"] == dfCleanedFlights["id_airline"]
dfFlightsAirlines = dfAirlines.join(dfCleanedFlights, joinExpr, "fullouter")

cols = ["flight_number", "tail_number", "date", "day_of_week", "airline", "origin_airport", "destination_airport", "distance",
        "scheduled_departure", "departure_time", "wheels_off", "scheduled_time", "air_time", "wheels_on", "scheduled_arrival",
        "arrival_time", "diverted", "cancelled", "cancellation_reason", "air_system_delay", "security_delay", "airline_delay",
        "late_aircraft_delay", "weather_delay"]
dfFlightsAirlinesNew = dfFlightsAirlines.select(*cols)

dfFlightsAirlinesNew.show()
dfFlightsAirlinesNew.printSchema()

dfAirports.show()
dfAirports.printSchema()

tempJoin1 = dfFlightsAirlinesNew.join(dfAirports, dfFlightsAirlinesNew["origin_airport"] == dfAirports["iata_code"], "left")
dfOriginAirportAgg = tempJoin1 \
                        .groupBy(col("airline"), col("airport")) \
                        .agg(sum(col("air_system_delay")).alias("total_air_system_delay"),
                             sum("security_delay").alias("total_security_delay"),
                             sum("airline_delay").alias("total_airline_delay"),
                             sum("late_aircraft_delay").alias("total_late_aircraft_delay"),
                             sum("weather_delay").alias("total_weather_delay"))
# dfOriginAirportAgg.show()

tempJoin2 = dfFlightsAirlinesNew.join(dfAirports, dfFlightsAirlinesNew["destination_airport"] == dfAirports["iata_code"], "left")
dfDestinationAirportAgg = tempJoin2 \
                        .groupBy(col("airline"), col("airport")) \
                        .agg(sum(col("air_system_delay")).alias("total_air_system_delay"),
                             sum("security_delay").alias("total_security_delay"),
                             sum("airline_delay").alias("total_airline_delay"),
                             sum("late_aircraft_delay").alias("total_late_aircraft_delay"),
                             sum("weather_delay").alias("total_weather_delay"))
# dfDestinationAirportAgg.show()


# Load Data to Hadoop HDFS & Local for Validations
partitionDate = datetime.today().strftime("%Y%m%d")
# Write CSV to local
dfFlightsAirlinesNew.write.csv(os.path.join(projectDir, f"output/FlightsAirlinesFact_{partitionDate}"),
                                    mode='overwrite',
                                    header=True)

dfAirports.write.csv(os.path.join(projectDir, f"output/AirportsDim_{partitionDate}"),
                                    mode='overwrite',
                                    header=True)

# Write Parquet to Hadoop HDFS
dfFlightsAirlinesNew.write.parquet(f"hdfs://hadoop:9000/output/FlightsAirlinesFact_{partitionDate}", 
                                   partitionBy='airline',
                                   mode='overwrite')

dfAirports.write.parquet(f"hdfs://hadoop:9000/output/AirportsDim_{partitionDate}", 
                                   partitionBy='iata_code',
                                   mode='overwrite')

dfOriginAirportAgg.write.parquet(f"hdfs://hadoop:9000/output/Data Mart/OriginAirport_{partitionDate}", 
                                   partitionBy=['airline', 'airport'],
                                   mode='overwrite')

dfDestinationAirportAgg.write.parquet(f"hdfs://hadoop:9000/output/Data Mart/DestinationAirport_{partitionDate}", 
                                   partitionBy=['airline', 'airport'],
                                   mode='overwrite')