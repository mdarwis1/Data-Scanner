import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def histogram(df, column):
    fig, ax = plt.subplots(figsize=(6, 4))
    
    ax.hist(df[column].dropna())

    ax.set_title(f"Distribution of {column}")
    ax.set_xlabel(column)
    ax.set_ylabel("Frequency")

    return fig

def scatterplot(df, x_column, y_column):
    fig, ax = plt.subplots(figsize=(6, 4))

    ax.scatter(df[x_column], df[y_column])

    ax.set_title(f"{y_column} vs {x_column}")
    ax.set_xlabel(x_column)
    ax.set_ylabel(y_column)

    return fig

def bar_graph(df, column):
    fig, ax = plt.subplots(figsize=(6, 4))

    df[column].value_counts().plot(kind="bar", ax=ax)

    ax.set_title(f"{column} Frequency")
    ax.set_xlabel(column)
    ax.set_ylabel("Count")

    return fig

def box_plot(df, column):
    fig, ax = plt.subplots(figsize=(6, 4))

    ax.boxplot(df[column].dropna())

    ax.set_title(f"Distribution of {column}")
    ax.set_ylabel(column)

    return fig

def recommend_visuals(df):

    recommendations = []

    # get numeric columns
    numeric_columns = df.select_dtypes(include=np.number).columns.tolist()

    # get categorical columns
    categorical_columns = df.select_dtypes(
        include=["object", "category"]
    ).columns.tolist()

    # numeric columns --> histogram
    for column in numeric_columns:

        # skip ID columns
        if "id" in column.lower():
            continue

        recommendations.append({
            "type": "Histogram",
            "columns": [column],
            "priority": 1,
            "reason": (
                f"Shows the distribution of {column}, "
                "including where values are concentrated."
            )
        })

    # numeric columns --> box plot
    for column in numeric_columns:

        # skip ID columns
        if "id" in column.lower():
            continue

        recommendations.append({
            "type": "Box Plot",
            "columns": [column],
            "priority": 1,
            "reason": (
                f"Shows the spread of {column} "
                "and may possibly help identify potential outliers."
            )
        })

    # using nested loop to compare each numeric column with column after that
    for i in range(len(numeric_columns)):
        for j in range(i + 1, len(numeric_columns)):

            x = numeric_columns[i]
            y = numeric_columns[j]

            # skip ID columns
            if "id" in x.lower() or "id" in y.lower():
                continue

            # calculate correlation to determine strength of relationship
            correlation = df[x].corr(df[y])

            if pd.isna(correlation):
                continue

            # storing strength of relationship
            strength = abs(correlation)

            # only recommend meaningful/strong relationships
            if strength >= 0.6:
                recommendations.append({
                    "type": "Scatterplot",
                    "columns": [x, y],
                    "correlation": round(correlation, 2),
                    "priority": 3,
                    "reason": (
                        f"{x} and {y} have a strong "
                        f"correlation ({correlation:.2f}), "
                        "so a scatterplot may possibly show their relationship."
                    )
                })

            elif strength >= 0.4:
                recommendations.append({
                    "type": "Scatterplot",
                    "columns": [x, y],
                    "correlation": round(correlation, 2),
                    "priority": 2,
                    "reason": (
                        f"{x} and {y} have a moderate "
                        f"correlation ({correlation:.2f}), "
                        "so a scatterplot may possibly reveal a relationship."
                    )
                })

    # categorical vs numeric
    for categorical in categorical_columns:

        # don't graph columns with tons of categories
        if df[categorical].nunique() > 10:
            continue

        recommendations.append({
            "type": "Bar Graph",
            "columns": [categorical],
            "priority": 2,
            "reason": (
                f"Shows how frequently each category "
                f"appears in {categorical}."
            )
        })

            
    # priority recommendation system
    recommendations.sort(

        # lambda creates tiny temp function 
        key=lambda x: x["priority"],
        reverse=True
    )

    return recommendations


