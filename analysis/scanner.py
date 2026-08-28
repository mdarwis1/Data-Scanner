import pandas as pd
import numpy as np

df = pd.read_csv('test_data/scanner_test_dataset.csv')

# Getting rows/columns of dataset
def get_dimensions(df):
    rows, columns = df.shape

    return {
        'rows': rows,
        'columns': columns,
    }


# storing data type and number of missing values for each column in df
def column_info(df): 
    info = {}

    for column in df.columns:
        info[column] = {
            "data_type": str(df[column].dtype),
            "missing_values": int(df[column].isna().sum())
        }

    return info 

def get_missing(df):
    # double .sum() sums missing values in each column and then sums that values again for entire df
    missing_values_count = df.isna().sum().sum()
    missing_values = f"Missing Values: {missing_values_count}"

    #multiplying rows x columns to get number of cells
    total_cells = df.shape[0] * df.shape[1]
    missing_values_percent_calc = (missing_values_count/total_cells) * 100
    missing_values_percent = f"{missing_values_percent_calc:.2f}%"
    return missing_values, missing_values_percent

def get_duplicates(df):
    duplicate_count = int(df.duplicated().sum())
    total_rows = len(df)
    duplicate_percent_calc = (duplicate_count/total_rows) * 100
    duplicate_percent = f"{duplicate_percent_calc:.2f}%"

    return duplicate_count, duplicate_percent

print(df)
print(get_dimensions(df))
print(column_info(df))
print(get_missing(df))
print(get_duplicates(df))