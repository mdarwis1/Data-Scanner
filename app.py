import streamlit as st
import pandas as pd

st.title("Data Scanner")
st.write("My Streamlit app is working!")

uploaded_file = st.file_uploader("Upload a CSV file", type="csv")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

tab1, tab2, tab3 = st.tabs(["Overview", "Problems", "Recommendations"])

with tab1:
    st.header("Dataset Overview")
    # dimensions, column info, missing values, duplicates, etc.
    

with tab2:
    st.header("Problems Detected")
    # outliers, mixed dtypes, whitespace, capitalization, etc.

with tab3:
    st.header("Recommendations")
    # cleaning recommendations and buttons