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

df = pd.read_csv("test_data/scanner_overview_test_2.csv")

# states holding versions of dataset
if "original_df" not in st.session_state:
    st.session_state.original_df = df.copy()

if "current_df" not in st.session_state:
    st.session_state.current_df = df.copy()

if "edit_history" not in st.session_state:
    st.session_state.edit_history = []

# always use current dataset to analyze
df = st.session_state.current_df

# adds edit change to history of edits list
def record_edit(action, column=None, method=None,
                cells_changed=0, rows_removed=0):

    st.session_state.edit_history.append({
        "Action": action,
        "Column": column if column is not None else "—",
        "Method": method if method is not None else "—",
        "Cells Changed": cells_changed,
        "Rows Removed": rows_removed
    })

# streamlit tabs
overview_tab, problems_tab, visuals_tab, cleaned_tab = st.tabs(
    ["Overview", "Problems", "Visualizations", "Cleaned Dataset"]
)

with overview_tab:

    st.header("Dataset Overview")

    # overview with different states
    original_df = st.session_state.original_df

    overview = scanner.data_overview(original_df)
    stat_results = stats.stat_overview(original_df)
    
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

    stat_results = stats.stat_overview(original_df)

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
                    width='stretch'
                )

                # cleaning buttons for numeric columns
                if pd.api.types.is_numeric_dtype(
                    st.session_state.current_df[column]
                ):

                    col1, col2 = st.columns(2)

                    with col1:
                        if st.button(
                            f"Fill with Mean",
                            key=f"mean_{column}"
                        ):
                            # save data before cleaning
                            before = st.session_state.current_df.copy()

                            # count missing values before cleaning
                            missing_before = (
                                before[column].isna().sum()
                            )

                            # apply existing cleaning function
                            st.session_state.current_df = (
                                cleaning.fill_missing_mean(
                                    before, column
                                )
                            )

                            # count missing values after cleaning
                            missing_after = (
                                st.session_state.current_df[column]
                                .isna()
                                .sum()
                            )

                            cells_changed = int(
                                missing_before - missing_after
                            )

                            # record edit in history list
                            if cells_changed > 0:
                                record_edit(
                                    action="Fill missing values",
                                    column=column,
                                    method="Mean",
                                    cells_changed=cells_changed
                                )

                            st.rerun()

                    with col2:
                        if st.button(
                            "Fill with Median",
                            key=f"median_{column}"
                        ):
                            before = st.session_state.current_df.copy()

                            missing_before = (
                                before[column].isna().sum()
                            )

                            st.session_state.current_df = (
                                cleaning.fill_missing_median(
                                    before, column
                                )
                            )

                            missing_after = (
                                st.session_state.current_df[column]
                                .isna()
                                .sum()
                            )

                            cells_changed = int(
                                missing_before - missing_after
                            )

                            if cells_changed > 0:
                                record_edit(
                                    action="Fill missing values",
                                    column=column,
                                    method="Median",
                                    cells_changed=cells_changed
                                )

                            st.rerun()
                            
                else:
                    if st.button(
                        "Fill with Unknown",
                        key=f"unknown_{column}"
                    ):
                        before = st.session_state.current_df.copy()
                        missing_before = before[column].isna().sum()

                        st.session_state.current_df = (
                            cleaning.fill_missing_unknown(
                                before, column
                            )
                        )

                        missing_after = (
                            st.session_state.current_df[column].isna().sum()
                        )

                        cells_changed = int(
                            missing_before - missing_after
                        )

                        if cells_changed > 0:
                            record_edit(
                                action="Fill missing values",
                                column=column,
                                method="Unknown",
                                cells_changed=cells_changed
                            )

                        st.rerun()

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
                    width='stretch'
                )
                
                action = st.selectbox(
                    "How would you like to fix these values?",
                    [
                        "Convert inconsistent values to missing values",
                        "Remove rows containing inconsistent values",
                        "Replace inconsistent values with a value of your choice"
                    ],
                    key=f"mixed_action_{column}"
                )

                replacement_value = None

                if action == (
                    "Replace inconsistent values with a value of your choice"
                ):
                    replacement_value = st.text_input(
                        "Replacement value",
                        key=f"mixed_replacement_{column}"
                    )

                if st.button(
                    "Apply Fix",
                    key=f"mixed_clean_{column}"
                ):
                    before = st.session_state.current_df.copy()

                    rows_before = len(before)

                    inconsistent_count = len(
                        info["inconsistent_cells"]
                    )

                    updated = cleaning.clean_mixed_dtypes(
                        before,
                        column,
                        action,
                        replacement_value
                    )

                    st.session_state.current_df = updated

                    rows_removed = rows_before - len(updated)

                    # for conversion/replacement, count affected cells.
                    cells_changed = (
                        inconsistent_count
                        if action != "Remove rows containing inconsistent values"
                        else 0
                    )

                    record_edit(
                        action="Clean mixed data types",
                        column=column,
                        method=action,
                        cells_changed=cells_changed,
                        rows_removed=rows_removed
                    )

                    st.rerun()

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
                    width='stretch'
                )
    
    # formatting
    formatting = recommendations.formatting_recommendations(
        st.session_state.current_df
    )

    if formatting:
        st.subheader("Formatting Issues")

        for column, issues in formatting.items():
            with st.expander(
                f"{column} — formatting issues"
            ):
                df = st.session_state.current_df

                # display detected issues
                for issue in issues:
                    if isinstance(issue, list):
                        st.write("**Affected values:**")
                        st.write(issue)
                    else:
                        st.write(f"**{issue}**")

                st.write("### Remove Whitespace")

                if st.button(
                    f"Remove whitespace from {column}",
                    key=f"whitespace_{column}"
                ):
                    before = st.session_state.current_df.copy()

                    # count cells that contain extra whitespace
                    cells_changed = int(
                        before[column].dropna().map(
                            lambda value: isinstance(value, str)
                            and value != value.strip()
                        ).sum()
                    )

                    # call cleaning whitespace function
                    st.session_state.current_df = (
                        cleaning.remove_whitespace(
                            before, column
                        )
                    )

                    if cells_changed > 0:
                        record_edit(
                            action="Fix formatting",
                            column=column,
                            method="Remove whitespace",
                            cells_changed=cells_changed
                        )

                    st.rerun()

                st.write("### Standardize Capitalization")

                values = (
                    df[column]
                    .dropna()
                    .astype(str)
                    .unique()
                    .tolist()
                )

                if values:
                    old_value = st.selectbox(
                        "Value to replace",
                        values,
                        key=f"old_value_{column}"
                    )

                    new_value = st.text_input(
                        "Replace with",
                        value=old_value,
                        key=f"new_value_{column}"
                    )

                    if st.button(
                        f"Replace value in {column}",
                        key=f"replace_value_{column}"
                    ):
                        before = st.session_state.current_df.copy()

                        # count matching cells before replacement
                        cells_changed = int(
                            (before[column] == old_value).sum()
                        )

                        # call capitalization function
                        st.session_state.current_df = (
                            cleaning.standardize_capitalization(
                                before,
                                column,
                                {old_value: new_value}
                            )
                        )

                        if old_value != new_value and cells_changed > 0:
                            record_edit(
                                action="Fix formatting",
                                column=column,
                                method=f"{old_value} → {new_value}",
                                cells_changed=cells_changed
                            )

                        st.rerun()

    else:
        st.success("No formatting issues detected.")
    # duplicates
    duplicates = recommendations.duplicate_recommendations(df)

    if duplicates["duplicate_count"] > 0:
        st.subheader("Duplicate Rows")

        st.write(duplicates["recommendation"])

        st.write("Duplicate rows:")

        st.dataframe(
            duplicates["duplicate_rows"],
            width='stretch'
        )

        if duplicates["duplicate_count"] > 0:
            option = st.selectbox(
                "Choose how to handle duplicates",
                [
                    "Keep first occurrence",
                    "Keep last occurrence",
                    "Remove all duplicate rows"
                ],
                key="duplicate_option"
            )

            if st.button(
                "Remove Duplicates",
                key="remove_duplicates"
            ):
                before = st.session_state.current_df.copy()
                rows_before = len(before)

                st.session_state.current_df = (
                    cleaning.remove_duplicate_rows(
                        before, option
                    )
                )

                rows_removed = (
                    rows_before -
                    len(st.session_state.current_df)
                )

                record_edit(
                    action="Remove duplicate rows",
                    method=option,
                    rows_removed=rows_removed
                )

                st.rerun()

    else:
        st.subheader("Duplicate Rows")
        st.write("No duplicate rows detected.")

with visuals_tab:
    st.header("Recommended Visualizations")

    st.write(
        "Data Scanner analyzed your dataset and recommends "
        "visualizations that may help you understand your data."
    )

    recommendations_list = charts.recommend_visuals(df)

    # group by graph type
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

    # show graph groups
    for graph_type, group in graph_groups.items():

        # don't display empty graph categories
        if not group:
            continue


        # graph type dropdown
        with st.expander(
            f"{graph_type} ({len(group)})"
        ):
            
            # loop through recommendations
            for i, recommendation in enumerate(group):

                columns = recommendation["columns"]

                reason = recommendation["reason"]

                priority = recommendation["priority"]

                # column name
                st.subheader(
                    " vs ".join(columns)
                    if len(columns) > 1
                    else columns[0]
                )

               # priority ranking system
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

                # reasoning/explanation
                st.write(
                    f"**Why:** {reason}"
                )

                # correlation
                if "correlation" in recommendation:

                    st.write(
                        f"**Correlation:** "
                        f"{recommendation['correlation']}"
                    )

               # button in each
                if st.button(
                    f"Use {graph_type}",
                    key=f"{graph_type}_{i}"
                ):
                    st.session_state.selected_visual = (
                        recommendation
                    )

                st.divider()

    # display recommendations
    if "selected_visual" in st.session_state:

        selected = st.session_state.selected_visual

        st.divider()

        st.header("Selected Visualization")

        graph_type = selected["type"]

        columns = selected["columns"]

       # histogram
        if graph_type == "Histogram":

            fig = charts.histogram(
                df,
                columns[0]
            )
            st.pyplot(fig)

       # box plot
        elif graph_type == "Box Plot":

            fig = charts.box_plot(
                df,
                columns[0]
            )
            st.pyplot(fig)

        # scatterplot
        elif graph_type == "Scatterplot":

            fig = charts.scatterplot(
                df,
                columns[0],
                columns[1]
            )
            st.pyplot(fig)

        # bar graph
        elif graph_type == "Bar Graph":

            fig = charts.bar_graph(
                df,
                columns[0]
            )
            st.pyplot(fig)

        # line graph
        elif graph_type == "Line Graph":

            fig = charts.line_plot(
                df,
                columns[0],
                columns[1]
            )
            st.pyplot(fig)

    # for MANUALLY creating graphs
    st.divider()
    st.header("Choose Your Own Visualization")
    st.write(
        "Want to explore something Data Scanner did not "
        "recommend? Choose a graph and columns yourself."
    )

    # get columns
    numeric_columns = df.select_dtypes(
        include=np.number
    ).columns.tolist()

    all_columns = df.columns.tolist()

    # graph types
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

with cleaned_tab:
    st.header("Cleaned Dataset")

    st.write(
        "Review the changes you have made and "
        "download your cleaned data."
    )

    # show edit history
    st.subheader("Cleaning History")

    if st.session_state.edit_history:

        history_df = pd.DataFrame(
            st.session_state.edit_history
        )

        st.dataframe(
            history_df,
            width="stretch"
        )

    else:
        st.info(
            "No cleaning actions have been performed yet."
        )

    # show current dataset
    st.subheader("Current Dataset")

    st.dataframe(
        st.session_state.current_df,
        width="stretch"
    )

    # download the cleaned dataset
    cleaned_csv = (
        st.session_state.current_df
        .to_csv(index=False)
        .encode("utf-8")
    )

    st.download_button(
        label="Download Cleaned Dataset",
        data=cleaned_csv,
        file_name="cleaned_dataset.csv",
        mime="text/csv"
    )

    # download cleaning history
    if st.session_state.edit_history:

        history_csv = (
            pd.DataFrame(st.session_state.edit_history)
            .to_csv(index=False)
            .encode("utf-8")
        )

        st.download_button(
            label="Download Cleaning History",
            data=history_csv,
            file_name="cleaning_history.csv",
            mime="text/csv"
        )