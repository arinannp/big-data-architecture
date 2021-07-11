import os
import great_expectations as ge
import pandas as pd
import psycopg2



projectDir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

conn = psycopg2.connect(host="postgres-db", port=5432, database="digitalskola", user="digitalskola", password="digitalskola")
dfAirlines = pd.read_sql_query("select * from airlines;", conn)
dfAirports = pd.read_sql_query("select * from airports;", conn)
dfFlights = pd.read_sql_query("select * from flights;", conn)
conn = None

dfAirlinesTest = ge.from_pandas(dfAirlines)
dfAirportsTest = ge.from_pandas(dfAirports)
dfFlightsTest = ge.from_pandas(dfFlights)


# docs check "https://docs.greatexpectations.io/en/latest/reference/glossary_of_expectations.html"

# dataframe airlines validation
check_null_airlines = dfAirlinesTest.expect_column_values_to_not_be_null(column='iata_code')
assert check_null_airlines['success'] == True, "DataFrame airlines kolom iata_code tidak boleh NULL"

check_unique_airlines = dfAirlinesTest.expect_column_values_to_be_unique(column='airline')
assert check_unique_airlines['success']==True, 'Kolom airline tidak boleh ada duplikat!'


# dataframe airports validation
check_null_airports = dfAirportsTest.expect_column_values_to_not_be_null(column='iata_code')
assert check_null_airports['success'] == True, "DataFrame airports kolom iata_code tidak boleh NULL"

check_unique_airports = dfAirportsTest.expect_column_values_to_be_unique(column='airport')
assert check_unique_airports['success']==True, 'Kolom airport tidak boleh ada duplikat!'


# dataframe flights validation
list_airline = dfAirlinesTest["iata_code"].tolist()
check_airlines_list = dfFlightsTest.expect_column_values_to_be_in_set(column='airline', value_set=list_airline)
assert check_airlines_list['success'] == True, \
        f'Terdapat airline yang tak dikenal, dengan kode: {set(check_airlines_list["result"]["partial_unexpected_list"])}'

list_airport = dfAirportsTest["iata_code"].tolist()
check_airports_list = dfFlightsTest.expect_column_values_to_be_in_set(column='origin_airport', value_set=list_airport)
assert check_airports_list['success'] == True, \
        f'Terdapat origin airport yang tak dikenal, dengan kode: {set(check_airports_list["result"]["partial_unexpected_list"])}'
        
check_airports_list = dfFlightsTest.expect_column_values_to_be_in_set(column='destination_airport', value_set=list_airport)
assert check_airports_list['success'] == True, \
        f'Terdapat destination airport yang tak dikenal, dengan kode: {set(check_airports_list["result"]["partial_unexpected_list"])}'
        
        
print("PASSED ALL TESTS")