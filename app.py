import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page.title("📊 Pretest vs Posttest Dashboard with Gain Analysis")st.set_page_config(page_title="Advanced LMS Dashboard", layout="wide")

st.info("Upload Pretest and Posttest Excel files (multiple allowed). Uses 75% passing rate.")

uploaded_files = st.file_uploader(
    "Upload Excel Files",
    type=['xlsx'],
    accept_multiple_files=True
)

if uploaded_files:
    all_data = []

    for file in uploaded_files:
        df = pd.read_excel(file, engine='openpyxl')

        # Identify test type automatically
        filename = file.name.lower()
        if 'pre' in filename:
            test_type = 'Pretest'
        elif 'post' in filename:
            test_type = 'Posttest'
        else:
            test_type = 'Unknown'

        df['Test'] = test_type
        df['Source_File'] = file.name

        all_data.append(df)

    data = pd.concat(all_data, ignore_index=True)

    st.subheader("📄 Combined Data Preview")
    st.dataframe(data.head())

    if 'Total points' not in data.columns:
        st.error("❌ Missing 'Total points' column.")
    else:
        # Compute passing threshold
        max_score = data['Total points'].max()


