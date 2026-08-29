import pandas as pd
import numpy as np

df = pd.read_csv('test_data/scanner_test_dataset.csv')


def get_mean(df):
    mean = df.mean(numeric_only = True)

    return mean

def get_median(df):
    median = df.median(numeric_only = True)

    return median


# number filter makes sure it doesn't apply min/max to categorical values too
def get_min(df):
    minimum = df.select_dtypes(include = np.number).min()

    return minimum

def get_max(df):
    maxiumum = df.select_dtypes(include = np.number).max()

    return maxiumum

def get_standard_dev(df):
    standard_deviation = df.select_dtypes(include = np.number).std()

    return standard_deviation

def get_unique_values(df):
    num_unique = df.nunique()
    
    return num_unique

# filters for categorical data and loops through to find frequencies for each categorical column
def get_frequencies(df):

    categorical_columns = df.select_dtypes(include=["object", "string", "category"]).columns

    frequencies = {}

    for column in categorical_columns:

        total_values = df[column].count()
        unique_values = df[column].nunique()

        # if all values are missig
        if total_values == 0:
            continue

        uniqueness_ratio = unique_values / total_values

        # fully unique column is 1, if column greater than 90% unique don't count frequencies for it (Ex. name, date, time, etc.)
        if uniqueness_ratio > 0.9:
            continue

        frequencies[column] = df[column].value_counts()

    return frequencies


print(get_mean(df))
print(get_median(df))
print(get_min(df))
print(get_max(df))
print(get_standard_dev(df))
print(get_unique_values(df))
print(get_frequencies(df))

print("Rows:", len(df))
print("Unique names:", df["Name"].nunique())
print("Uniqueness:", df["Name"].nunique() / len(df))
