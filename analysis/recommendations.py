import pandas as pd
import numpy as np


df = pd.read_csv('test_data/missing_values_test.csv')

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

def outlier_recommendations(df):
    outliers = get_outliers(df)

    

def analyze_distribution(df):
    numeric_columns = df.select_dtypes(include="number").columns

    distribution_info = {}

    # calculate skewness
    for column in numeric_columns:
        skewness = df[column].skew()

        distribution_info[column] = {
            "skewness": skewness
        }

    return distribution_info


def missing_value_recommendations(df):
    total_missing = {}

    for column in df:
        missing_count = df[column].isna().sum()

        # if there is missing value, check whether numerical or categorical and perform corresponding logic
        if missing_count > 0:
            if pd.api.types.is_numeric_dtype(df[column]):

                total_missing[column] = {
                    "missing_count": int(missing_count),
                    "type": "numerical"
                }
            else:
                total_missing[column] = {
                    "missing_count": int(missing_count),
                    "type": "categorical",
                    'recommendation': "Fill with 'Unknown'"
                }

            distribution = analyze_distribution(df)

            for column, info in distribution.items():
                skewness = info['skewness']

                if abs(skewness) <= 0.5:
                    recommendation = "mean"
                else:
                    recommendation = "median"


    return total_missing

print(get_outliers(df))
print(missing_value_recommendations(df))
