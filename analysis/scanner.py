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

