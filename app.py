import streamlit as st
import pandas as pd

from analysis import scanner
from analysis import stats
from analysis import recommendations
from analysis import cleaning

st.title("Data Scanner")

st.write("Upload a CSV to get started!")

df = pd.read_csv("test_data/scanner_all_tests.csv")

if "df" not in st.session_state:
    st.session_state.df = None

tab1, tab2, tab3 = st.tabs(
    ["Overview", "Problems", "Recommendations"]
)

with tab1:

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

with tab2:
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

with tab3:
    st.header("Recommendations")
    # cleaning recommendations and buttons