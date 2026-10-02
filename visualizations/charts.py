import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def histogram(df, column):
    fig, ax = plt.subplots()

    ax.hist(df[column].dropna())

    ax.set_title(f"Distribution of {column}")
    ax.set_xlabel(column)
    ax.set_ylabel("Frequency")

    return fig

def scatterplot(df, x_column, y_column):
    fig, ax = plt.subplots()

    ax.scatter(df[x_column], df[y_column])

    ax.set_title(f"{y_column} vs {x_column}")
    ax.set_xlabel(x_column)
    ax.set_ylabel(y_column)

    return fig

def bar_graph(df, column):
    fig, ax = plt.subplots()

    df[column].value_counts().plot(kind="bar", ax=ax)

    ax.set_title(f"{column} Frequency")
    ax.set_xlabel(column)
    ax.set_ylabel("Count")

    return fig

def box_plot(df, column):
    fig, ax = plt.subplots()

    ax.boxplot(df[column].dropna())

    ax.set_title(f"Distribution of {column}")
    ax.set_ylabel(column)

    return fig

def line_plot(df, x_column, y_column):
    fig, ax = plt.subplots()

    ax.plot(df[x_column], df[y_column])

    ax.set_title(f"{y_column} vs {x_column}")
    ax.set_xlabel(x_column)
    ax.set_ylabel(y_column)

    return fig


def correlation_heatmap(df):

    fig, ax = plt.subplots()

    data = df.drop(
        columns=[column for column in df.columns if "id" in column.lower()],
        errors="ignore"
    )

    correlation = data.select_dtypes(include="number").corr()

    sns.heatmap(correlation, annot=True, ax=ax)

    ax.set_title("Correlation Between Numeric Columns")

    return fig