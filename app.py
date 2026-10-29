import streamlit as st
import pandas as pd
import numpy as np

from analysis import scanner
from analysis import stats
from analysis import recommendations
from analysis import cleaning
from visualizations import charts

# widens entire page
st.set_page_config(layout="wide")


st.title("Data Scanner")

st.write("Upload a CSV to get started!")

col1, col2 = st.columns([1, 3])

with col1:
    uploaded_file = st.file_uploader(
        "Upload a CSV",
        type="csv"
    )

if uploaded_file is None:
    st.stop()

df = pd.read_csv(uploaded_file)
df["_original_row"] = range(2, len(df) + 2)

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

    st.markdown(
        "<h2 style='text-align: center;'>Dataset Overview</h2>",
        unsafe_allow_html=True
    )
    # always use original dataset for overview
    original_df = st.session_state.original_df

    overview = scanner.data_overview(original_df)
    stat_results = stats.stat_overview(original_df)
    
    left, center, right = st.columns([2, 1, 2])

    with center:
        st.markdown(
            "<h3 style='text-align: center;'>Dimensions</h3>",
            unsafe_allow_html=True
        )

        col1, spacer, col2 = st.columns([10, 20, 10])

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

    st.dataframe(stat_results["numerical_stats"])

    st.subheader("Unique Values")

    for column, count in stat_results["unique_values"].items():
        st.write(f"**{column}:** {count} unique values")

    st.subheader("Categorical Frequencies")

    for column, counts in stat_results["frequencies"].items():
        st.write(f"**{column}**")
        st.dataframe(counts)

with problems_tab:
    st.markdown(
        "<h2 style='text-align: center;'>Problems Detected</h2>",
        unsafe_allow_html=True
    )

    # missing values
    missing = recommendations.missing_value_recommendations(df)

    if missing:
        st.subheader("Missing Values")

        df = st.session_state.current_df

        columns_to_clean = [
            column for column in df.columns
            if column != "_original_row"
        ]

        for column, info in missing.items():
            left, right = st.columns([2, 1])

            with left:
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
                    
                    # choose which missing cells to clean
                    current_df = st.session_state.current_df

                    missing_row_options = {
                        f"CSV row {int(current_df.loc[index, '_original_row'])}": index
                        for index in current_df.index
                        if pd.isna(current_df.loc[index, column])
                    }

                    cleaning_scope = st.radio(
                        "Which cells should be cleaned?",
                        ["All missing cells", "Choose specific rows"],
                        key=f"scope_{column}"
                    )

                    selected_indices = []

                    if cleaning_scope == "Choose specific rows":
                        selected_labels = st.multiselect(
                            "Select rows with missing values",
                            options=list(missing_row_options.keys()),
                            key=f"selected_rows_{column}"
                        )

                        selected_indices = [
                            missing_row_options[label]
                            for label in selected_labels
                        ]

                    # fill with mean/median
                    if pd.api.types.is_numeric_dtype(current_df[column]):
                        col1, col2 = st.columns(2)

                        with col1:
                            if st.button("Fill with Mean", key=f"mean_{column}"):
                                before = st.session_state.current_df.copy()
                                missing_before = int(before[column].isna().sum())

                                if cleaning_scope == "All missing cells":
                                    updated = cleaning.fill_missing_mean(
                                        before.copy(), column
                                    )
                                else:
                                    updated = before.copy()
                                    mean_value = updated[column].mean()

                                    for index in selected_indices:
                                        if pd.isna(updated.loc[index, column]):
                                            updated.loc[index, column] = mean_value

                                missing_after = int(updated[column].isna().sum())
                                cells_changed = missing_before - missing_after

                                if cells_changed > 0:
                                    st.session_state.current_df = updated
                                    record_edit(
                                        action="Fill missing values",
                                        column=column,
                                        method="Mean",
                                        cells_changed=cells_changed
                                    )
                                elif cleaning_scope == "Choose specific rows":
                                    st.warning("Select at least one missing cell.")

                                st.rerun()


                        with col2:
                            if st.button("Fill with Median", key=f"median_{column}"):
                                
                                before = st.session_state.current_df.copy()
                                missing_before = int(before[column].isna().sum())

                                if cleaning_scope == "All missing cells":
                                    updated = cleaning.fill_missing_median(before.copy(), column)
                            
                                else:
                                    updated = before.copy()
                                    median_value = updated[column].median()

                                    for index in selected_indices:
                                        if pd.isna(updated.loc[index, column]):
                                            updated.loc[index, column] = median_value

                                cells_changed = (
                                    missing_before - int(updated[column].isna().sum())
                                )

                                if cells_changed > 0:
                                    st.session_state.current_df = updated
                                    record_edit(
                                        action="Fill missing values",
                                        column=column,
                                        method="Median",
                                        cells_changed=cells_changed
                                    )
                                elif cleaning_scope == "Choose specific rows":
                                    st.warning("Select at least one missing cell.")

                                st.rerun()

                    # fill with "Unknown"
                    else:
                        if st.button("Fill with Unknown", key=f"unknown_{column}"):
                            before = st.session_state.current_df.copy()

                            if cleaning_scope == "All missing cells":
                                updated = cleaning.fill_missing_unknown(
                                    before.copy(), column
                                )
                            else:
                                updated = before.copy()

                                for index in selected_indices:
                                    if pd.isna(updated.loc[index, column]):
                                        updated.loc[index, column] = "Unknown"

                            cells_changed = int(
                                before[column].isna().sum()
                                - updated[column].isna().sum()
                            )

                            if cells_changed > 0:
                                st.session_state.current_df = updated
                                record_edit(
                                    action="Fill missing values",
                                    column=column,
                                    method="Unknown",
                                    cells_changed=cells_changed
                                )
                            elif cleaning_scope == "Choose specific rows":
                                st.warning("Select at least one missing cell.")

                            st.rerun()
    else:
        left, right = st.columns([1,3])

        with left:
            st.success("No missing values detected.")


    # mixed dtypes
    mixed = recommendations.mixed_dtypes_detection(df)

    if mixed:
        st.subheader("Mixed Data Types")

        for column, info in mixed.items():

            # make expander narrower
            left, right = st.columns([2, 1])

            with left:
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
                        width="stretch"
                    )

                    # make dropdown narrower 
                    dropdown_col, empty_col = st.columns([2, 1])

                    with dropdown_col:
                        action = st.selectbox(
                            "How would you like to fix these values?",
                            [
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
    else:
        left, right = st.columns([1,3])
        
        with left:
            st.success("No mixed datatypes detected.")

    # outliers
    outliers = recommendations.outlier_recommendations(
        st.session_state.current_df
    )

    if outliers:
        st.subheader("Potential Outliers")

        for column, info in outliers.items():
            left, right = st.columns([2, 1])

            with left:
                with st.expander(
                    f"{column} — "
                    f"{info['outlier_count']} potential outlier(s)"
                ):
                    st.write(
                        f"**Recommendation:** {info['recommendation']}"
                    )

                    st.write("Potential outlier values:")

                    st.dataframe(
                        pd.DataFrame({
                            "CSV Row": info["outlier_rows"],
                            "Value": info["outlier_values"]
                        }),
                        width="stretch",
                        hide_index=True
                    )

                    # choose how to handle outliers
                    action = st.selectbox(
                        "How would you like to handle these outliers?",
                        [
                            "Remove selected rows",
                            "Replace with chosen value",
                        ],
                        key=f"outlier_action_{column}"
                    )

                    # select individual rows
                    selected_rows = st.multiselect(
                        "Select the CSV rows to clean",
                        options=info["outlier_rows"],
                        default=info["outlier_rows"],
                        key=f"outlier_rows_{column}"
                    )

                    # ask for a value if the user chooses to replace 
                    replacement_value = None

                    if action == "Replace with chosen value":
                        replacement_value = st.number_input(
                            "Replacement value",
                            value=float(
                                st.session_state.current_df[column].median()
                            ),
                            key=f"outlier_value_{column}"
                        )

                    if st.button(
                        "Apply Outlier Cleaning",
                        key=f"apply_outlier_{column}"
                    ):
                        if not selected_rows:
                            st.warning(
                                "Please select at least one outlier row."
                            )
                        else:
                            before = (
                                st.session_state.current_df.copy()
                            )

                            updated, changed_count = (
                                cleaning.outlier_cleaning(
                                    before,
                                    column=column,
                                    action=action,
                                    selected_rows=selected_rows,
                                    replacement_value=replacement_value
                                )
                            )

                            if changed_count > 0:
                                st.session_state.current_df = updated

                                record_edit(
                                    action="Handle outliers",
                                    column=column,
                                    method=action,
                                    cells_changed=(
                                        changed_count
                                        if action != "Remove selected rows"
                                        else 0
                                    ),
                                    rows_removed=(
                                        changed_count
                                        if action == "Remove selected rows"
                                        else 0
                                    )
                                )

                                st.success(
                                    f"Processed {changed_count} outlier row(s)."
                                )
                                st.rerun()
                            else:
                                st.info(
                                    "No selected outlier rows were changed."
                                )

    else:
        left, right = st.columns([1,3])
        
        with left:
            st.success("No potential outliers detected.")

    
    # formatting
    formatting = recommendations.formatting_recommendations(
        st.session_state.current_df
    )

    if formatting:
        st.subheader("Formatting Issues")

        for column, issues in formatting.items():
            left, right = st.columns([2, 1])

            with left:
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
                            value=old_value.strip(),
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

                            cleaned_value = new_value.strip()

                            # call capitalization function
                            st.session_state.current_df = (
                                cleaning.standardize_capitalization(
                                    before,
                                    column,
                                    {old_value: cleaned_value}
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
        left, right = st.columns([1,3])
        
        with left:
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
            dropdown_col, empty_col = st.columns([2, 1])

            with dropdown_col:
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
        left, right = st.columns([1,3])
        
        with left:
            st.success("No duplicate rows detected.")

with visuals_tab:
    st.markdown(
        "<h2 style='text-align: center;'>Recommended Visualizations</h2>",
        unsafe_allow_html=True
    )
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

        # narrow visualization expanders
        expander_col, empty_col = st.columns([2, 1])

        with expander_col:
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

            left, center, right = st.columns([1, 2, 1])

            with center:
                st.pyplot(fig)

       # box plot
        elif graph_type == "Box Plot":

            fig = charts.box_plot(
                df,
                columns[0]
            )

            left, center, right = st.columns([1, 2, 1])

            with center:
                st.pyplot(fig)

        # scatterplot
        elif graph_type == "Scatterplot":

            fig = charts.scatterplot(
                df,
                columns[0],
                columns[1]
            )

            left, center, right = st.columns([1, 2, 1])

            with center:
                st.pyplot(fig)

        # bar graph
        elif graph_type == "Bar Graph":

            fig = charts.bar_graph(
                df,
                columns[0]
            )
            
            left, center, right = st.columns([1, 2, 1])

            with center:
                st.pyplot(fig)

        # line graph
        elif graph_type == "Line Graph":

            fig = charts.line_plot(
                df,
                columns[0],
                columns[1]
            )
            
            left, center, right = st.columns([1, 2, 1])

            with center:
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
    dropdown_col, empty_col = st.columns([2, 1])

    with dropdown_col:
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

        dropdown_col, empty_col = st.columns([2, 1])

        with dropdown_col:
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

            left, center, right = st.columns([1, 2, 1])

            with center:
                st.pyplot(fig)

    elif manual_graph_type == "Box Plot":

        dropdown_col, empty_col = st.columns([2, 1])

        with dropdown_col:
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

            left, center, right = st.columns([1, 2, 1])

            with center:
                st.pyplot(fig)

    elif manual_graph_type == "Bar Graph":

        dropdown_col, empty_col = st.columns([2, 1])

        with dropdown_col:
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

            left, center, right = st.columns([1, 2, 1])

            with center:
                st.pyplot(fig)

    elif manual_graph_type == "Scatterplot":

        dropdown_col, empty_col = st.columns([2, 1])

        with dropdown_col:
            x_column = st.selectbox(
                "X-axis",
                numeric_columns,
                key="manual_scatter_x"
            )

        dropdown_col, empty_col = st.columns([2, 1])

        with dropdown_col:
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

            left, center, right = st.columns([1, 2, 1])

            with center:
                st.pyplot(fig)

    elif manual_graph_type == "Line Graph":

        dropdown_col, empty_col = st.columns([2, 1])

        with dropdown_col:
            x_column = st.selectbox(
                "X-axis",
                all_columns,
                key="manual_line_x"
            )

        dropdown_col, empty_col = st.columns([2, 1])

        with dropdown_col:
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

            left, center, right = st.columns([1, 2, 1])

            with center:
                st.pyplot(fig)
                
with cleaned_tab:
    st.markdown(
        "<h2 style='text-align: center;'>Cleaned Dataset</h2>",
        unsafe_allow_html=True
    )
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
        message_col, empty_col = st.columns([2, 1])

        with message_col:
            st.info(
                "No cleaning actions have been performed yet."
            )

    # show current dataset
    st.subheader("Current Dataset")

    st.dataframe(
        st.session_state.current_df.drop(
            columns=["_original_row"], errors="ignore"
        ).reset_index(drop=True),
        width="stretch",
        hide_index=True
    )

    # download the cleaned dataset
    cleaned_csv = (
        st.session_state.current_df
        .drop(columns=["_original_row"], errors="ignore")
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