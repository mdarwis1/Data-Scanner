# Data Scanner

## Link to App
https://data-scanner.streamlit.app/

## Overview

Web application that takes a user uploaded CSV and analyzes the dataset for basic statistics, potential problems that need to be cleaned, and appropriate visualization options. User is given recommendations for different methods to resolve dataset issues. Explanations are given to help user better understand how exactly data is getting modified to improve accuracy. While cleaning, the scanner tracks a history of dataset changes and displays a real-time CSV that can then be downloaded as a new, cleaned dataset.

## Features

### Dataset Overview

- Displays dimensions and columns within dataset
- Identifies how many missing values present
- Identifies how many duplicate rows present
- Displays basic statistics (mean, median, standard deviation, etc.)
- Lists out number of unique values per column
- Lists out categorical frequencies

### Problems

#### Missing Values

- Displays rows with missing values
- Calculates distribution/skew of dataset
- For numerical missing values: recommends mean or median based on distribution of data
- For categorical missing values: recommends filling with "Unknown"
- User can specify cleaning all missing cells or choose the specific rows affected

#### Mixed Data Types

- Determines what the majority data type in dataset is
- Any values that don't match are flagged
- User can choose to remove or replace affected values

#### Potential Outliers

- Outlier cutoffs calculated mathematically with IQR
- Values that fall outside the upper and lower cutoffs flagged as potential outliers
- User can choose to remove affected rows or replace affected values
- User can specify cleaning all rows or choose a specific row affected

#### Formatting Issues

- Detects leading/trailing whitespace
- Allows user to remove whitespace from affected values
- Also detects mismatch capitalization
- User given list of values found with different variations and can choose which version of the word is the correct one
- User can choose what string to replace the affected one with

#### Duplicate Rows

- Identifies duplicate rows in dataset
- Gives user option to keep first occurrence, keep last occurrence, or remove all occurrences

### Visualizations

- Recommends certain graphs based on current dataset
- Offers scatterplot, histogram, box plot, and bar graph
- Prioritizes some recommendations higher based on a system of calculated correlations and categorical vs. numerical types
- Has a manual graph feature where user can pick columns to create their own graph instead

### Cleaned Dataset

- Displays history of every change made to the dataset
- Shows a real-time version of the current dataset that gets updated after every change
- Option to download cleaned dataset
- Option to download cleaning history

## Technologies Used

- Python
- Pandas
- NumPy
- Matplotlib
- Streamlit

## What I Learned

- Expanded knowledge of basic Python functions and methods
- Learned more about data, data science, and manipulating data with Python
- Working with Python libraries (Pandas, NumPy, and Matplotlib) at a more advanced level
- Utilizing dictionary organization for storing information
- Using Streamlit for front end implementation of Python and UI
