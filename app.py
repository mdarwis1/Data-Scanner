import streamlit as st
import pandas as pd
import numpy as np

from analysis import scanner
from analysis import stats
from analysis import recommendations
from analysis import cleaning
from visualizations import charts

st.title("Data Scanner")

st.write("Upload a CSV to get started!")

df = pd.read_csv("test_data/visualizations_test.csv")

if "df" not in st.session_state:
    st.session_state.df = None

overview_tab, problems_tab, visuals_tab = st.tabs(
    ["Overview", "Problems", "Visualizations"]
)

with overview_tab:

    st.header("Dataset Overview")

    # Basic overview
    overview = scanner.data_overview(df)

    st.subheader("Dimensions")

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Rows", overview["dimensions"]["rows"])

    with col2:
        st.metric("Columns", overview["dimensions"]["columns"])

    st.subheader("Column Info")
    st.dataframe(overview["column_info"])

    st.subheader("Missing Data")
    st.write(f"Missing Values: {overview['missing_count']}")
    st.write(f"Missing Percentage: {overview['missing_percent']}")

    st.subheader("Duplicates")
    st.write(f"Duplicate Rows: {overview['duplicate_count']}")
    st.write(f"Duplicate Percentage: {overview['duplicate_percent']}")

    # Statistics
    st.subheader("Numerical Statistics")

    stat_results = stats.stat_overview(df)

    st.dataframe(stat_results["numerical_stats"])

    st.subheader("Unique Values")

    for column, count in stat_results["unique_values"].items():
        st.write(f"**{column}:** {count} unique values")

    st.subheader("Categorical Frequencies")

    for column, counts in stat_results["frequencies"].items():
        st.write(f"**{column}**")
        st.dataframe(counts)

with problems_tab:
    st.header("Problems Detected")

    # missing values
    missing = recommendations.missing_value_recommendations(df)

    if missing:
        st.subheader("Missing Values")

        for column, info in missing.items():
            with st.expander(
                f"{column} — {info['missing_count']} missing"
            ):
                st.write(f"**Type:** {info['type']}")
                st.write(f"**Recommendation:** {info['recommendation']}")

                st.write("Affected rows:")
                st.dataframe(
                    df[df[column].isna()],
                    use_container_width=True
                )

   
    # mixed dtypes
    mixed = recommendations.mixed_dtypes_detection(df)

    if mixed:
        st.subheader("Mixed Data Types")

        for column, info in mixed.items():
            with st.expander(
                f"{column} — mixed data types"
            ):
                st.write(
                    f"**Types found:** "
                    f"{', '.join(info['types_present'])}"
                )

                st.write(
                    f"**Majority type:** {info['majority_type']}"
                )

                st.write("Inconsistent cells:")

                st.dataframe(
                    pd.DataFrame(info["inconsistent_cells"]),
                    use_container_width=True
                )

   # outliers
    outliers = recommendations.outlier_recommendations(df)

    if outliers:
        st.subheader("Potential Outliers")

        for column, info in outliers.items():
            with st.expander(
                f"{column} — "
                f"{info['outlier_count']} potential outlier(s)"
            ):
                st.write(
                    f"**Recommendation:** "
                    f"{info['recommendation']}"
                )

                st.write("Potential outlier values:")

                st.dataframe(
                    pd.DataFrame({
                        "Value": info["outlier_values"]
                    }),
                    use_container_width=True
                )

    # formatting
    formatting = recommendations.formatting_recommendations(df)

    if formatting:
        st.subheader("Formatting Issues")

        for column, issues in formatting.items():
            with st.expander(
                f"{column} — formatting issues"
            ):
                for issue in issues:

                    # Lists contain the affected values
                    if isinstance(issue, list):
                        st.write("Affected values:")
                        st.write(issue)

                    # Strings contain recommendations
                    else:
                        st.write(f"**{issue}**")

    # duplicates
    duplicates = recommendations.duplicate_recommendations(df)

    if duplicates["duplicate_count"] > 0:
        st.subheader("Duplicate Rows")

        st.write(duplicates["recommendation"])

        st.write("Duplicate rows:")

        st.dataframe(
            duplicates["duplicate_rows"],
            use_container_width=True
        )

    else:
        st.subheader("Duplicate Rows")
        st.write("No duplicate rows detected.")

with visuals_tab:
    st.header("Recommended Visualizations")

    st.write(
        "Data Scanner analyzed your dataset and recommends "
        "visualizations that may help you understand your data."
    )


    # -----------------------------------------------------
    # GET RECOMMENDATIONS
    # -----------------------------------------------------

    recommendations_list = charts.recommend_visuals(df)


    # -----------------------------------------------------
    # GROUP BY GRAPH TYPE
    # -----------------------------------------------------

    graph_groups = {

        "Scatterplot": [],

        "Histogram": [],

        "Box Plot": [],

        "Bar Graph": [],

        "Line Graph": []

    }


    for recommendation in recommendations_list:

        graph_type = recommendation["type"]

        if graph_type in graph_groups:

            graph_groups[graph_type].append(
                recommendation
            )


    # -----------------------------------------------------
    # SHOW GRAPH GROUPS
    # -----------------------------------------------------

    for graph_type, group in graph_groups.items():

        # Don't display empty graph categories
        if not group:
            continue


        # Graph type dropdown
        with st.expander(
            f"{graph_type} ({len(group)})"
        ):


            # Loop through recommendations
            for i, recommendation in enumerate(group):

                columns = recommendation["columns"]

                reason = recommendation["reason"]

                priority = recommendation["priority"]


                # -------------------------
                # COLUMN NAME
                # -------------------------

                st.subheader(
                    " vs ".join(columns)
                    if len(columns) > 1
                    else columns[0]
                )


                # -------------------------
                # PRIORITY
                # -------------------------

                if priority == 3:

                    st.write(
                        "⭐ **High Priority**"
                    )

                elif priority == 2:

                    st.write(
                        "**Recommended**"
                    )

                else:

                    st.write(
                        "**Optional**"
                    )


                # -------------------------
                # REASON
                # -------------------------

                st.write(
                    f"**Why:** {reason}"
                )


                # -------------------------
                # CORRELATION
                # -------------------------

                if "correlation" in recommendation:

                    st.write(
                        f"**Correlation:** "
                        f"{recommendation['correlation']}"
                    )


                # -------------------------
                # USE BUTTON
                # -------------------------

                if st.button(
                    f"Use {graph_type}",
                    key=f"{graph_type}_{i}"
                ):

                    st.session_state.selected_visual = (
                        recommendation
                    )


                st.divider()


    # =====================================================
    # DISPLAY SELECTED RECOMMENDATION
    # =====================================================

    if "selected_visual" in st.session_state:

        selected = st.session_state.selected_visual

        st.divider()

        st.header("Selected Visualization")


        graph_type = selected["type"]

        columns = selected["columns"]


        # -------------------------
        # HISTOGRAM
        # -------------------------

        if graph_type == "Histogram":

            fig = charts.histogram(
                df,
                columns[0]
            )

            st.pyplot(fig)


        # -------------------------
        # BOX PLOT
        # -------------------------

        elif graph_type == "Box Plot":

            fig = charts.box_plot(
                df,
                columns[0]
            )

            st.pyplot(fig)


        # -------------------------
        # SCATTERPLOT
        # -------------------------

        elif graph_type == "Scatterplot":

            fig = charts.scatterplot(
                df,
                columns[0],
                columns[1]
            )

            st.pyplot(fig)


        # -------------------------
        # BAR GRAPH
        # -------------------------

        elif graph_type == "Bar Graph":

            fig = charts.bar_graph(
                df,
                columns[0]
            )

            st.pyplot(fig)


        # -------------------------
        # LINE GRAPH
        # -------------------------

        elif graph_type == "Line Graph":

            fig = charts.line_plot(
                df,
                columns[0],
                columns[1]
            )

            st.pyplot(fig)


    # =====================================================
    # MANUAL VISUALIZATION
    # =====================================================

    st.divider()

    st.header("Choose Your Own Visualization")

    st.write(
        "Want to explore something Data Scanner did not "
        "recommend? Choose a graph and columns yourself."
    )


    # -----------------------------------------------------
    # GET COLUMNS
    # -----------------------------------------------------

    numeric_columns = df.select_dtypes(
        include=np.number
    ).columns.tolist()

    all_columns = df.columns.tolist()


    # -----------------------------------------------------
    # GRAPH TYPE
    # -----------------------------------------------------

    manual_graph_type = st.selectbox(
        "Visualization type",

        [
            "Histogram",
            "Box Plot",
            "Scatterplot",
            "Bar Graph",
            "Line Graph"
        ],

        key="manual_graph_type"
    )


    # =====================================================
    # MANUAL HISTOGRAM
    # =====================================================

    if manual_graph_type == "Histogram":

        column = st.selectbox(
            "Column",

            numeric_columns,

            key="manual_histogram_column"
        )


        if st.button(
            "Create Histogram",
            key="create_histogram"
        ):

            fig = charts.histogram(
                df,
                column
            )

            st.pyplot(fig)


    # =====================================================
    # MANUAL BOX PLOT
    # =====================================================

    elif manual_graph_type == "Box Plot":

        column = st.selectbox(
            "Column",

            numeric_columns,

            key="manual_box_column"
        )


        if st.button(
            "Create Box Plot",
            key="create_box"
        ):

            fig = charts.box_plot(
                df,
                column
            )

            st.pyplot(fig)


    # =====================================================
    # MANUAL BAR GRAPH
    # =====================================================

    elif manual_graph_type == "Bar Graph":

        column = st.selectbox(
            "Column",

            all_columns,

            key="manual_bar_column"
        )


        if st.button(
            "Create Bar Graph",
            key="create_bar"
        ):

            fig = charts.bar_graph(
                df,
                column
            )

            st.pyplot(fig)


    # =====================================================
    # MANUAL SCATTERPLOT
    # =====================================================

    elif manual_graph_type == "Scatterplot":

        x_column = st.selectbox(
            "X-axis",

            numeric_columns,

            key="manual_scatter_x"
        )


        y_column = st.selectbox(
            "Y-axis",

            numeric_columns,

            key="manual_scatter_y"
        )


        if st.button(
            "Create Scatterplot",
            key="create_scatter"
        ):

            fig = charts.scatterplot(
                df,
                x_column,
                y_column
            )

            st.pyplot(fig)


    # =====================================================
    # MANUAL LINE GRAPH
    # =====================================================

    elif manual_graph_type == "Line Graph":

        x_column = st.selectbox(
            "X-axis",

            all_columns,

            key="manual_line_x"
        )


        y_column = st.selectbox(
            "Y-axis",

            numeric_columns,

            key="manual_line_y"
        )


        if st.button(
            "Create Line Graph",
            key="create_line"
        ):

            fig = charts.line_plot(
                df,
                x_column,
                y_column
            )

            st.pyplot(fig)