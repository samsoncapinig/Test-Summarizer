
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Assessment Summary", layout="wide")

st.title("📊 Pretest/Posttest Summarizer")

st.info("Upload one or more Excel files. The app combines all data and computes summary using 75% passing rate.")

uploaded_files = st.file_uploader("Upload Excel Files", type=['xlsx'], accept_multiple_files=True)

if uploaded_files:
    combined_df = pd.DataFrame()
    
    for file in uploaded_files:
        df = pd.read_excel(file, engine='openpyxl')
        df['Source_File'] = file.name
        combined_df = pd.concat([combined_df, df], ignore_index=True)

    st.subheader("Combined Data Preview")
    st.dataframe(combined_df.head())

    if 'Total points' not in combined_df.columns:
        st.error("Column 'Total points' not found in uploaded files.")
    else:
        max_score = combined_df['Total points'].max()
        passing_score = max_score * 0.75

        combined_df['Passed'] = combined_df['Total points'] >= passing_score

        # Summary per file (subject-level proxy)
        summary = combined_df.groupby('Source_File').agg(
            Total_Takers=('Total points','count'),
            Passers=('Passed','sum')
        ).reset_index()

        summary['Failed'] = summary['Total_Takers'] - summary['Passers']
        summary['Percentage Passing'] = (summary['Passers'] / summary['Total_Takers']) * 100

        summary.rename(columns={'Source_File':'Subjects Taken'}, inplace=True)

        st.subheader("📈 Summary Results")
        st.dataframe(summary)

        # Download
        output_file = "multi_summary.xlsx"
        summary.to_excel(output_file, index=False, engine='openpyxl')

        with open(output_file, "rb") as f:
            st.download_button("⬇️ Download Excel Summary", f, file_name="multi_summary.xlsx")

        st.success("Analysis complete ✅")


# =============================
# FOOTER
# =============================

from datetime import datetime

st.divider()

col_pic, col_text = st.columns([1, 6])

with col_pic:
    st.image("samson.png", width=80)

with col_text:
    st.markdown(
        f"""
        **Developed by Sir Sam**   
        Pretest/Postest Summarizer • SDO Masbate City  
        © {datetime.now().year} . All rights reserved.
        """
    )
