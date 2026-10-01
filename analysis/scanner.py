import pandas as pd
import numpy as np
from . import stats

df = pd.read_csv('test_data/scanner_overview_test_2.csv')

# Getting rows/columns of dataset
def get_dimensions(df):
    rows, columns = df.shape

    return {
        'rows': rows,
        'columns': columns,
    }

# storing data type and number of missing values for each column in table
def column_info(df):
    info = []

    for column in df.columns:
        info.append({
            "Column": column,
            "Data Type": str(df[column].dtype),
            "Missing Values": int(df[column].isna().sum())
        })

    return pd.DataFrame(info)

def get_missing(df):
    # double .sum() sums missing values in each column and then sums that values again for entire df
    missing_count = df.isna().sum().sum()

    #multiplying rows x columns to get number of cells
    total_cells = df.shape[0] * df.shape[1]
    missing_values_percent_calc = (missing_count/total_cells) * 100
    missing_values_percent = f"{missing_values_percent_calc:.2f}%"
    return missing_count, missing_values_percent

def get_duplicates(df):
    duplicate_count = int(df.duplicated().sum())
    total_rows = len(df)
    duplicate_percent_calc = (duplicate_count/total_rows) * 100
    duplicate_percent = f"{duplicate_percent_calc:.2f}%"

    return duplicate_count, duplicate_percent

def data_overview(df):
        dimensions = get_dimensions(df)
    
        missing_count, missing_percent = get_missing(df)
    
        duplicate_count, duplicate_percent = get_duplicates(df)
    
        return {
            "dimensions": dimensions,
            "column_info": column_info(df),
            "missing_count": missing_count,
            "missing_percent": missing_percent,
            "duplicate_count": duplicate_count,
            "duplicate_percent": duplicate_percent
        }

#     print("Dataset Overview:")

#     print(f"\nRows: {dimensions['rows']}")
#     print(f"Columns: {dimensions['columns']}")

#     print("\nColumn Info:")

#     print(column_info(df))

#     print("\nMissing Data:")
#     print(f"Missing Values: {missing_count}")

#     print(f"Missing Percentage: {missing_percent}")

#     print("\nDuplicates:")
#     print(f"Duplicate Rows: {duplicate_count}")
#     print(f"Duplicate Percentage: {duplicate_percent}")

#     stats.stat_overview(df)


# data_overview(df)



