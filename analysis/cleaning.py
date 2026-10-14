import pandas as pd
import numpy as np
from . import recommendations

df = pd.read_csv('test_data/scanner_overview_test_2.csv')

# fill missing values
def fill_missing_mean(df, column):
    df[column] = df[column].fillna(df[column].mean())
    return df

def fill_missing_median(df, column):
    df[column] = df[column].fillna(df[column].median())
    return df

def fill_missing_unknown(df, column):
    df[column] = df[column].fillna("Unknown")
    return df

# convert/remove/replace mixed datatypes
def clean_mixed_dtypes(df, column, action, replacement_value=None):
    
    mixed_dtypes = recommendations.mixed_dtypes_recommendations(df)
    inconsistent_cells = mixed_dtypes[column]["inconsistent_cells"]

    if action == "Convert inconsistent values to missing values":

        # converts the inconsistent cell to NaN
        for cell in inconsistent_cells:
            row = cell["row"] - 2
            df.loc[row, column] = np.nan
    elif action == "Convert inconsistent values to strings":
        for cell in inconsistent_cells:
            original_row = cell["row"]

            if "_original_row" in df.columns:
                matching_indices = df.index[
                    df["_original_row"] == original_row
                ]
                if len(matching_indices) > 0:
                    df.loc[matching_indices[0], column] = str(cell["value"])
            else:
                row_index = original_row - 2
                if row_index in df.index:
                    df.loc[row_index, column] = str(cell["value"])

    elif action == "Remove rows containing inconsistent values":
        
        rows_to_remove = []

        # finds which rows have inconsistent cells
        for cell in inconsistent_cells:
            row = cell["row"] - 2
            rows_to_remove.append(row)

        # drops the ones stored in array above
        df = df.drop(index=rows_to_remove)

    elif action == "Replace inconsistent values with a value of your choice":
        
        for cell in inconsistent_cells:
            row = cell["row"] - 2

            # user inputted value
            df.loc[row, column] = replacement_value

    return df

# fix formatting
def remove_whitespace(df, column):
    df[column] = df[column].str.strip()
    return df

def standardize_capitalization(df, column, replacements):
    for old_value, new_value in replacements.items():
        df[column] = df[column].replace(old_value, new_value)

    return df

# remove duplicates
def remove_duplicate_rows(df, option):
    compare_columns = [
        column for column in df.columns
        if column != "_original_row"
    ]

    if option == "Keep first occurrence":
        return df.drop_duplicates(
            subset=compare_columns,
            keep="first"
        )

    elif option == "Keep last occurrence":
        return df.drop_duplicates(
            subset=compare_columns,
            keep="last"
        )

    elif option == "Remove all duplicate rows":
        return df.drop_duplicates(
            subset=compare_columns,
            keep=False
        )

    return df

# remove/replace outliers
def outlier_cleaning(
    df,
    column,
    action,
    selected_rows=None,
    replacement_value=None
):
    df = df.copy()

    outliers = recommendations.outlier_detection(df)

    if column not in outliers:
        return df, 0

    # Get the exact original CSV rows containing outliers
    outlier_rows = outliers[column]["outlier_rows"]

    # If no rows were selected, process all outliers
    if selected_rows is None:
        selected_rows = outlier_rows

    selected_rows = set(selected_rows) & set(outlier_rows)

    if not selected_rows:
        return df, 0

    # match selected CSV rows to the current DataFrame
    if "_original_row" in df.columns:
        mask = df["_original_row"].isin(selected_rows)
    else:
        mask = df.index.isin([row - 2 for row in selected_rows])

    outlier_indices = df.index[mask]
    changed_count = len(outlier_indices)

    if action == "Remove selected rows":
        df = df.drop(index=outlier_indices)

    elif action == "Replace with chosen value":
        if replacement_value is None:
            raise ValueError("Please provide a replacement value.")

        df.loc[outlier_indices, column] = replacement_value

    elif action == "Replace with median":
        median_value = df[column].median()
        df.loc[outlier_indices, column] = median_value

    else:
        raise ValueError("Invalid outlier-cleaning action.")

    return df, changed_count
