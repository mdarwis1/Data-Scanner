import pandas as pd
import numpy as np

df = pd.read_csv('test_data/scanner_overview_test_2.csv')

def fill_missing_mean(df, column):
    df[column] = df[column].fillna(df[column].mean())
    return df

def fill_missing_median(df, column):
    df[column] = df[column].fillna(df[column].median())
    return df

def fill_missing_known(df, column):
    df[column] = df[column].fillna("Unknown")
    return df