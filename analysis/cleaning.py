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
    df = df.copy()

    mixed_dtypes = recommendations.mixed_dtypes_detection(df)
   
    # check that the selected column was detected
    if column not in mixed_dtypes:
        return df

    inconsistent_cells = mixed_dtypes[column]["inconsistent_cells"]

    rows_to_clean = []

    for cell in inconsistent_cells:
        original_row = cell["row"]

        if "_original_row" in df.columns:
            matching_indices = df.index[
                df["_original_row"] == original_row
            ]
            rows_to_clean.extend(matching_indices.tolist())
        else:
            row_index = original_row - 2
            if row_index in df.index:
                rows_to_clean.append(row_index)

    # avoid duplicates
    rows_to_clean = list(set(rows_to_clean))

    if action == "Remove rows containing inconsistent values":
        df = df.drop(index=rows_to_clean)

    elif action == "Replace inconsistent values with a value of your choice":
        if replacement_value is None or not str(replacement_value).strip():
            raise ValueError("Please provide a non-empty replacement value.")

        for row_index in rows_to_clean:
            df.loc[row_index, column] = replacement_value

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

    # get original CSV rows containing outliers
    outlier_rows = outliers[column]["outlier_rows"]

    # if no rows were selected, process all outliers
    if selected_rows is None:
        selected_rows = outlier_rows

    selected_rows = set(selected_rows) & set(outlier_rows)

    if not selected_rows:
        return df, 0

    # match selected CSV rows to the current DataFrame
    if "_original_row" in df.columns:
        mask = df["_original_row"].isin(selected_rows)
    else:
        mask = df.index.isin(selected_rows)

    outlier_indices = df.index[mask]
    changed_count = len(outlier_indices)

    if action == "Remove selected rows":
        df = df.drop(index=outlier_indices)

    elif action == "Replace with chosen value":
        if replacement_value is None:
            raise ValueError("Please provide a replacement value.")

        df.loc[outlier_indices, column] = replacement_value

    else:
        raise ValueError("Invalid outlier-cleaning action.")

    return df, changed_count
