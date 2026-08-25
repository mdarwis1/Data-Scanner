import pandas as pd
import numpy as np

df = pd.read_csv('test_data/basic_test.csv')


def get_mean(df):
    mean = df.mean(numeric_only = True)

    return mean

def get_median(df):
    median = df.median(numeric_only = True)

    return median


print(get_mean(df))
print(get_median(df))
