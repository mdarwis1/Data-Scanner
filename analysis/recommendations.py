import pandas as pd
import numpy as np


## Outlier Detection

# calculating IQR for outlier cutoffs
def outlier_detection(df):

    numeric_columns = [
        column
        for column in df.select_dtypes(include="number").columns
        if column != "_original_row"
    ]

    # dictionary to associate column w outliers
    total_outliers = {}

    for column in numeric_columns:

        Q1 = df[column].quantile(0.25)
        Q3 = df[column].quantile(0.75)
        IQR = Q3 - Q1

        lower_cutoff = Q1 - (IQR * 1.5)
        upper_cutoff = Q3 + (IQR * 1.5)

        # identifies outlier rows
        outlier_mask = (
            (df[column] < lower_cutoff)
            | (df[column] > upper_cutoff)
        )

        # keep rows containing outliers
        outlier_data = df.loc[outlier_mask]

        if not outlier_data.empty:
            total_outliers[column] = {
                "outlier_values": outlier_data[column].tolist(),

                # original CSV row numbers
                "outlier_rows": (
                    outlier_data["_original_row"].tolist()
                    if "_original_row" in df.columns
                    else outlier_data.index.tolist()
                )
            }

    return total_outliers

def outlier_recommendations(df):
    outliers = outlier_detection(df)
    outlier_recs = {}

    for column, info in outliers.items():
        outlier_count = len(info["outlier_values"])

        if outlier_count == 1:
            recommendation = (
                "1 potential outlier detected. Review it "
                "and consider removing or changing it."
            )
        else:
            recommendation = (
                "Multiple potential outliers detected. Review them "
                "and consider removing or changing them."
            )

        outlier_recs[column] = {
            "outlier_count": outlier_count,
            "outlier_values": info["outlier_values"],
            "outlier_rows": info["outlier_rows"],
            "recommendation": recommendation
        }

    return outlier_recs
    

def analyze_distribution(df):

    numeric_columns = [
        column
        for column in df.select_dtypes(include="number").columns
        if column != "_original_row"
    ]

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

    outliers = outlier_detection(df)

    for column in df.columns:
        if column == "_original_row":
            continue

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

def mixed_dtypes_detection(df):

    mixed_dtypes = {}

    for column in df.columns:

        if column == "_original_row":
            continue

        # stores values of each numeric/string value
        numeric_values = []
        non_numeric_values = []

        # loop through every cell in every column
        for index, value in df[column].items():

            # skip missing/null values, don't affect dtype analysis
            if pd.isna(value):
                continue

            # if value can be converted to number, store it as numeric
            try:
                float(value)
                numeric_values.append({
                    "row": (
                        int(df.loc[index, "_original_row"])
                        if "_original_row" in df.columns
                        else int(index) + 2
                    ),
                    "value": value,
                    "type": "numeric"
                })
            # if doesn't work, store it as string
            except:
                non_numeric_values.append({
                    "row": (
                        int(df.loc[index, "_original_row"])
                        if "_original_row" in df.columns
                        else int(index) + 2
                    ),
                    "value": value,
                    "type": "string"
                })

        # total up counts for each dtype
        numeric_count = len(numeric_values)
        non_numeric_count = len(non_numeric_values)

        # storing which is majority vs minority dtype, for determining which value is considered "weird" in the column
     
        # only report if contains both dtypes
        if numeric_count > 0 and non_numeric_count > 0:

            if numeric_count > non_numeric_count:
                majority_type = "numeric"
                inconsistent_cells = non_numeric_values

            elif non_numeric_count > numeric_count:
                majority_type = "string"
                inconsistent_cells = numeric_values

            else:
                majority_type = "mixed"
                inconsistent_cells = numeric_values + non_numeric_values

            mixed_dtypes[column] = {
                "types_present": ["numeric", "string"],
                "majority_type": majority_type,
                "inconsistent_cells": inconsistent_cells
            }

    return mixed_dtypes

def mixed_dtypes_recommendations(df):

    recommendations = {}

    mixed_dtypes = mixed_dtypes_detection(df)

    for column, info in mixed_dtypes.items():

        recommendations[column] = []

        if info["majority_type"] == "numeric":
            recommendations[column].append(
                "Convert inconsistent values to missing values"
            )
            recommendations[column].append(
                "Remove rows containing inconsistent values"
            )
            recommendations[column].append(
                "Replace inconsistent values with a value of your choice"
            )

        elif info["majority_type"] == "string":
            recommendations[column].append(
                "Convert inconsistent values to strings"
            )
            recommendations[column].append(
                "Remove rows containing inconsistent values"
            )
            recommendations[column].append(
                "Replace inconsistent values with a value of your choice"
            )
            
    return recommendations

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

def formatting_recommendations(df):
    recommendations = {}

    whitespace = whitespace_detection(df)
    capitalization = capitalization_detection(df)

    for column in df:
        if column == "_original_row":
            continue
        issues = []

        if column in whitespace:
            issues.append(whitespace[column])
            issues.append("Remove leading or trailing whitespace.")

        if column in capitalization:
            issues.append(capitalization[column])
            issues.append("Inconsistent capitalization. Consider standardizing capitalization.")

        if issues:
            recommendations[column] = issues

    return recommendations

def duplicate_recommendations(df):

    # ID makes every row unique, detects ID column and ignores it
    columns_to_ignore = []

    for column in df.columns:
        if "id" in column.lower() or column == "_original_row":
            columns_to_ignore.append(column)

    data = df.drop(columns=columns_to_ignore)

    # sums up the booleans returned from .duplicated()
    duplicate_mask = data.duplicated(keep=False)
    duplicate_count = int(duplicate_mask.sum())   
     
    duplicate_percent = (
        duplicate_count / len(df) * 100
        # can't divide by 0 if no rows
        if len(df) > 0 else 0
        )
    
    duplicate_rows = df[duplicate_mask]

    # no duplicates
    if duplicate_count == 0:
        recommendation = "No duplicate rows detected."

    else:
        recommendation = (
            f"The dataset contains {duplicate_count} duplicate rows "
            f"({duplicate_percent:.2f}% of all rows). "
            "Review them to determine whether they are intentional before removing them."
        )
  
    return {
        "duplicate_count": duplicate_count,
        "duplicate_percentage": duplicate_percent,  
        "duplicate_rows": duplicate_rows,
        "recommendation": recommendation
    }



#print(missing_value_recommendations(df))
#print(outlier_recommendations(df))

# print(mixed_dtypes_recommendations(df))
#print(whitespace_detection(df))
#print(capitalization_detection(df))

#print(duplicate_recommendations(df))
#print(formatting_recommendations(df))
