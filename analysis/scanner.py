import pandas as pd
import numpy as np

df = pd.read_csv('test_data/basic_test.csv')

# Getting rows/columns of dataset
def get_dimensions(df):
    rows, columns = df.shape

    return {
        'rows': rows,
        'columns': columns,
    }

def get_mean(df):
    mean = df.mean(numeric_only = True)

    return mean

def get_median(df):
    median = df.median(numeric_only = True)

    return median

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
    missing_values = df.isna().sum().sum()

    return missing_values

print(df)
print(get_dimensions(df))
print(column_info(df))
#print(get_mean(df))
#print(get_median(df))
print(get_missing(df))