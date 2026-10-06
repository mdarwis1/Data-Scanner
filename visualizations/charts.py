import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

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

def recommend_visuals(df):

    recommendations = []

    # get numeric columns
    numeric_columns = df.select_dtypes(include=np.number).columns.tolist()

    # get categorical columns
    categorical_columns = df.select_dtypes(
        include=["object", "category"]
    ).columns.tolist()

    # numeric columns --> histogram
    for numeric in numeric_columns:

        # skip ID columns
        if "id" in numeric.lower():
            continue

        recommendations.append({
            "type": "histogram",
            "column": numeric,
            "reason": f"A histogram shows the distribution of {numeric}."
        })

    # numeric columns --> box plot
    for numeric in numeric_columns:

        # skip ID columns
        if "id" in numeric.lower():
            continue

        recommendations.append({
            "type": "box",
            "column": numeric,
            "reason": f"A box plot shows the spread of {numeric} and can highlight potential outliers."
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
                "type": "scatter",
                "x": x,
                "y": y,
                "correlation": round(correlation, 2),
                "reason": (
                    f"{x} and {y} have a strong correlation "
                    f"(r = {round(correlation, 2)})."
                )
            })

            elif strength >= 0.4:
                recommendations.append({
                "type": "scatter",
                "x": x,
                "y": y,
                "correlation": round(correlation, 2),
                "reason": (
                    f"{x} and {y} have a moderate correlation "
                    f"(r = {round(correlation, 2)})."
                )
            })

    # categorical vs numeric
    for categorical in categorical_columns:

        # don't graph columns with tons of categories
        if df[categorical].nunique() > 10:
            continue

        for numeric in numeric_columns:

            # Don't use IDs
            if "id" in numeric.lower():
                continue

            recommendations.append({
                "type": "bar",
                "x": categorical,
                "y": numeric,
                "reason": f"Bar graphs are good for comparing categorical groups. Compare {numeric} across {categorical}"
            })

    return recommendations

