import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Assessment Summary", layout="wide")

st.image("logo.gif", width=1400)

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

        # Summary per file
        summary = combined_df.groupby('Source_File').agg(
            Total_Takers=('Total points','count'),
            Passers=('Passed','sum')
        ).reset_index()

        summary['Failed'] = summary['Total_Takers'] - summary['Passers']
        summary['Percentage Passing'] = (summary['Passers'] / summary['Total_Takers']) * 100

        summary.rename(columns={'Source_File':'Subjects Taken'}, inplace=True)

        st.subheader("📈 Summary Results")
        st.dataframe(summary)

        # =============================
        # 📊 GRAPHS SECTION
        # =============================
        st.subheader("📊 Visual Analysis")

        # ✅ 1. Bar Chart (Pass vs Fail per Subject)
        st.markdown("### Passers vs Failed per Subject")
        fig1, ax1 = plt.subplots()
        summary.set_index('Subjects Taken')[['Passers', 'Failed']].plot(kind='bar', ax=ax1)
        ax1.set_ylabel("Number of Students")
        ax1.set_title("Pass vs Fail per Subject")
        st.pyplot(fig1)

        # ✅ 2. Passing Rate Chart (%)
        st.markdown("### Passing Rate (%) per Subject")
        fig2, ax2 = plt.subplots()
        summary.set_index('Subjects Taken')['Percentage Passing'].plot(kind='bar', ax=ax2)
        ax2.set_ylabel("Percentage (%)")
        ax2.set_title("Passing Rate per Subject")
        st.pyplot(fig2)

        # ✅ 3. Overall Pie Chart
        st.markdown("### Overall Pass vs Fail Distribution")
        total_pass = summary['Passers'].sum()
        total_fail = summary['Failed'].sum()

        fig3, ax3 = plt.subplots()
        ax3.pie(
            [total_pass, total_fail],
            labels=['Pass', 'Fail'],
            autopct='%1.1f%%',
            startangle=90
        )
        ax3.set_title("Overall Passing Distribution")
        st.pyplot(fig3)

        # =============================
        # DOWNLOAD
        # =============================
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
