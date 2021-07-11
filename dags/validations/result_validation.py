import os
import great_expectations as ge
import pandas as pd
from datetime import datetime
import glob



project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
partition_date = datetime.today().strftime("%Y%m%d")

files_fact_table = glob.glob(os.path.join(project_dir, f"output/FlightsAirlinesFact_{partition_date}") + "/*.csv")
list_csv_fact = []
for filename in files_fact_table:
    df = pd.read_csv(filename)
    list_csv_fact.append(df)
dfFact = pd.concat(list_csv_fact)

files_dims_table = glob.glob(os.path.join(project_dir, f"output/AirportsDim_{partition_date}") + "/*.csv")
list_csv_dims = []
for filename in files_dims_table:
    df = pd.read_csv(filename)
    list_csv_dims.append(df)
dfDims = pd.concat(list_csv_dims)

dfFactTest = ge.from_pandas(dfFact)
dfDimsTest = ge.from_pandas(dfDims)


# docs check "https://docs.greatexpectations.io/en/latest/reference/glossary_of_expectations.html"

# dataframe fact table validation
check_column_flight_number = dfFactTest.expect_column_to_exist(column='flight_number')
assert check_column_flight_number['success']==True, 'Kolom flight_number harus ada!'

check_null_flight_number = dfFactTest.expect_column_values_to_not_be_null(column='flight_number')
assert check_null_flight_number['success'] == True, "Kolom flight_number tidak boleh NULL"

check_total_row_fact = dfFactTest.expect_table_row_count_to_equal(value=5000)
assert check_total_row_fact['success'] == True, "Jumlah total row fact table seharusnya 5000"


# dataframe dimension table validation
check_unique_iata_code = dfDimsTest.expect_column_values_to_be_unique(column='iata_code')
assert check_unique_iata_code['success']==True, 'Kolom iata_code tidak boleh ada duplikat!'

check_null_iata_code = dfDimsTest.expect_column_values_to_not_be_null(column='iata_code')
assert check_null_iata_code['success'] == True, "Kolom iata_code tidak boleh NULL"

check_value_country = dfDimsTest.expect_column_values_to_be_in_set(column='country', value_set=["USA"])
assert check_value_country['success'] == True, \
        f'Terdapat country yang tak dikenal, dengan kode: {set(check_value_country["result"]["partial_unexpected_list"])}'

check_total_row_dims = dfDimsTest.expect_table_row_count_to_equal(value=322)
assert check_total_row_fact['success'] == True, "Jumlah total row dim table seharusnya 322"


print("PASSED ALL TESTS")