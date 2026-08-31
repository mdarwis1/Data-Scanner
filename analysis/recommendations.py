import pandas as pd
import numpy as np
import scanner


df = pd.read_csv('test_data/outliers_test.csv')

## Outlier Detection

# calculating IQR for outlier cutoffs
def get_outliers(df):
    numeric_columns = df.select_dtypes(include="number").columns

    # dictionary to associate column w outliers
    total_outliers = {}

    for column in numeric_columns:

        Q1 = df[column].quantile(0.25)
        Q3 = df[column].quantile(0.75)
        IQR = Q3 - Q1

        lower_cutoff = Q1 - (IQR * 1.5)
        upper_cutoff = Q3 + (IQR * 1.5)

        # gets the rows where a column has a potential outlier
        outliers = df[(df[column] < lower_cutoff) | (df[column] > upper_cutoff)]
        
        # don't include columns with 0 outliers
        if not outliers.empty:
            total_outliers[column] = outliers[column].tolist()

    return total_outliers

def missing_values_analysis(df):
    total_missing = {}

    for column in df:
        missing_count = df[column].isna().sum()

        if missing_count > 0:
            total_missing[column] = missing_count

    return total_missing

print(get_outliers(df))
print(missing_values_analysis(df))
