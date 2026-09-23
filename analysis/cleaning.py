import pandas as pd
import numpy as np

df = pd.read_csv('test_data/scanner_overview_test_2.csv')

# fill missing values
def fill_missing_mean(df, column):
    df[column] = df[column].fillna(df[column].mean())
    return df

def fill_missing_median(df, column):
    df[column] = df[column].fillna(df[column].median())
    return df

def fill_missing_known(df, column):
    df[column] = df[column].fillna("Unknown")
    return df

# convert mixed datatypes

# fix formatting
def remove_whitespace(df, column):
    df[column] = df[column].str.strip()
    return df

def standardize_capitalization(df, column, replacements):
    for old_value, new_value in replacements.items():
        df[column] = df[column].replace(old_value, new_value)

    return df

# remove duplicates

# remove/replace outliers