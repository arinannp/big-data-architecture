import os
import psycopg2
import pandas as pd

project_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dags")


print(project_dir)
print(f'python {project_dir}/validations/source_validation.py')
print(f'python {project_dir}/validations/result_validation.py')

conn = psycopg2.connect(host="postgres-db", port=5432, database="digitalskola", user="digitalskola", password="digitalskola")
dfAirlines = pd.read_sql_query("select * from airlines;", conn)
dfAirports = pd.read_sql_query("select * from airports;", conn)
dfFlights = pd.read_sql_query("select * from flights;", conn)
conn = None

print(dfAirlines.head())
print(dfAirports.head())
print(dfFlights.head())