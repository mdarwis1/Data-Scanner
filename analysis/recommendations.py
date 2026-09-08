import pandas as pd
import numpy as np


df = pd.read_csv('test_data/mixed_dtypes_test.csv')

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

    outlier_recs = {}

    for column in outliers:

        outlier_count = len(outliers[column])

        if outlier_count == 1:
            recommendation = "1 potential outlier detected. Review it and consider removing or changing it."

        else:
            recommendation = "Multiple potential outliers detected. Review them and consider removing or changing them."

        outlier_recs[column] = {
            'outlier_count': outlier_count,
            'outlier_values': outliers[column],
            'recommendation': recommendation
        }

    return outlier_recs
    

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

    distribution = analyze_distribution(df)

    outliers = get_outliers(df)

    for column in df:
        missing_count = df[column].isna().sum()

        # if there is missing value, check whether numerical or categorical and perform corresponding logic
        if missing_count > 0:
            if pd.api.types.is_numeric_dtype(df[column]):

                # mean good for evenly distributed skew w no outliers
                # median good for skewed data
                skewness = distribution[column]['skewness']

                # if outliers, use median
                if column in outliers:
                    recommendation = "Fill with median"
                elif abs(skewness) <= 0.5:
                    recommendation = "Fill with mean"
                else:
                    recommendation = "Fill with median"

                total_missing[column] = {
                    "missing_count": int(missing_count),
                    "type": "numerical",
                    "recommendation": recommendation
                }
            else:
                total_missing[column] = {
                    "missing_count": int(missing_count),
                    "type": "categorical",
                    'recommendation': "Fill with 'Unknown'"
                }

    return total_missing

def analyze_mixed_dtypes(df):

    mixed_dtypes = {}

    for column in df.columns:

        # stores values of each numeric/string value
        numeric_values = []
        non_numeric_values = []

        # loop through every cell in every column
        for value in df[column]:

            # skip missing/null values, don't affect dtype analysis
            if pd.isna(value):
                continue

            # if value can be converted to number, store it as numeric
            try:
                float(value)
                numeric_values.append(value)
            # if doesn't work, store it as string
            except:
                non_numeric_values.append(value)

        # total up counts for each dtype
        numeric_count = len(numeric_values)
        non_numeric_count = len(non_numeric_values)

        # storing which is majority vs minority dtype, for determining which value is considered "weird" in the column
     
        # only report if contains both dtypes
        if numeric_count > 0 and non_numeric_count > 0:

            if numeric_count > non_numeric_count:
                mixed_dtypes[column] = {
                    "majority_type": "numeric",
                    "minority_values": non_numeric_values
                }

            elif non_numeric_count > numeric_count:
                mixed_dtypes[column] = {
                    "majority_type": "string",
                    "minority_values": numeric_values
                }

            else:
                mixed_dtypes[column] = {
                    "majority_type": "mixed",
                    "minority_values": numeric_values + non_numeric_values
                }

    return mixed_dtypes

# print(missing_value_recommendations(df))
# print(outlier_recommendations(df))

print(analyze_mixed_dtypes(df))