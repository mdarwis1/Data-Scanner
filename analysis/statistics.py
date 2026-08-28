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


print(get_mean(df))
print(get_median(df))
print(get_min(df))
print(get_max(df))
print(get_standard_dev(df))


