import pandas as pd
import numpy as np

df = pd.read_csv('example.csv')

# Getting rows/columns of dataset
def get_dimensions(df):
    rows, columns = df.shape()

    return {
        'rows': rows,
        'columns': columns,
    }

def get_mean(df):
    mean = df.mean()

    return mean

def get_median(df):
    median = df.median()

    return median