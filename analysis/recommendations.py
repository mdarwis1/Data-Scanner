import pandas as pd
import numpy as np


df = pd.read_csv('test_data/duplicates_test.csv')

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

def whitespace_detection(df):
    white_space = {}

    for column in df:
        issues = []

        for value in df[column]:
            if isinstance(value, str):
                new_value = value.strip()
                if len(new_value) != len(value):
                    issues.append(value)

        if issues:
            white_space[column] = issues

    return white_space

def capitalization_detection(df):
    capitalization = {}

    for column in df:
        # only get unique values, not duplicates
        values = df[column].dropna().unique()

        # using groups to organize values that are same when capitalization ignored
        groups = {}

        for value in values:
            # compare values without capitalization to see if they're the same word
            if isinstance(value, str):
                lowercase_value = value.lower()

                if lowercase_value not in groups:
                    groups[lowercase_value] = []

                # associates the lowercase grouping word with all the variations present in dataset
                groups[lowercase_value].append(value)

        # loops through the variations within each group
        for key, variants in groups.items():
            # if more than 1 variant, capitalization error
            if len(variants) > 1:
                if column not in capitalization:
                    capitalization[column] = []

                capitalization[column].append(variants)

    return capitalization

def duplicate_recommendations(df):

    # ID makes every row unique, detects ID column and ignores it
    id_columns = []

    for column in df.columns:
        if "id" in column.lower():
            id_columns.append(column)

    data = df.drop(columns=id_columns)

    # sums up the booleans returned from .duplicated()
    duplicate_count = int(data.duplicated().sum())
    
    duplicate_percent = (duplicate_count / len(df)) * 100

    # no duplicates
    if duplicate_count == 0:
        recommendation = "No duplicate rows detected."

    # duplicates exist, but make up only small portion of data
    elif duplicate_percent < 10:
        recommendation = (
            "Potential duplicate rows detected. Review them and consider removing copies."
        )
    else:
        recommendation = (
            "A significant portion of the dataset contains duplicate rows. "
            "Review them to determine whether they are intentional before removing them."
        )
  
    return {
        "duplicate_count": duplicate_count,
        "duplicate_percentage": duplicate_percent,
        "recommendation": recommendation
    }



# print(missing_value_recommendations(df))
# print(outlier_recommendations(df))

#print(analyze_mixed_dtypes(df))
# print(whitespace_detection(df))
#print(capitalization_detection(df))

print(duplicate_recommendations(df))
