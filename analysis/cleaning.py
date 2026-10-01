import pandas as pd
import numpy as np
from . import recommendations

df = pd.read_csv('test_data/scanner_overview_test_2.csv')

# fill missing values
def fill_missing_mean(df, column):
    df[column] = df[column].fillna(df[column].mean())
    return df

def fill_missing_median(df, column):
    df[column] = df[column].fillna(df[column].median())
    return df

def fill_missing_unknown(df, column):
    df[column] = df[column].fillna("Unknown")
    return df

# convert/remove/replace mixed datatypes
def clean_mixed_dtypes(df, column, action, replacement_value=None):
    
    mixed_dtypes = recommendations.mixed_dtypes_recommendations(df)
    inconsistent_cells = mixed_dtypes[column]["inconsistent_cells"]

    if action == "Convert inconsistent values to missing values":

        # converts the inconsistent cell to NaN
        for cell in inconsistent_cells:
            row = cell["row"] - 2
            df.loc[row, column] = np.nan

    elif action == "Remove rows containing inconsistent values":
        
        rows_to_remove = []

        # finds which rows have inconsistent cells
        for cell in inconsistent_cells:
            row = cell["row"] - 2
            rows_to_remove.append(row)

        # drops the ones stored in array above
        df = df.drop(index=rows_to_remove)

    elif action == "Replace inconsistent values with a value of your choice":
        
        for cell in inconsistent_cells:
            row = cell["row"] - 2

            # user inputted value
            df.loc[row, column] = replacement_value

    return df

# fix formatting
def remove_whitespace(df, column):
    df[column] = df[column].str.strip()
    return df

def standardize_capitalization(df, column, replacements):
    for old_value, new_value in replacements.items():
        df[column] = df[column].replace(old_value, new_value)

    return df

# remove duplicates
def remove_duplicate_rows(df, option):
    if option == "Keep first occurrence":
        return df.drop_duplicates(keep="first")

    elif option == "Keep last occurrence":
        return df.drop_duplicates(keep="last")

    elif option == "Remove all duplicate rows":
        return df.drop_duplicates(keep=False)

    return df

# remove/replace outliers