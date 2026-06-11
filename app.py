
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Assessment Summary", layout="wide")

st.title("📊 Pretest/Posttest Summary Dashboard")

st.info("Upload MS Forms quiz Excel (like your sample). App auto-computes totals using 'Total points'. Passing rate = 75%.")

uploaded = st.file_uploader("Upload Excel File", type=['xlsx'])

if uploaded:
    df = pd.read_excel(uploaded, engine='openpyxl')

    st.subheader("Raw Data Preview")
    st.dataframe(df.head())

    # Detect score column
    if 'Total points' not in df.columns:
        st.error("Column 'Total points' not found.")
    else:
        max_score = df['Total points'].max()
        passing_score = max_score * 0.75

        df['Passed'] = df['Total points'] >= passing_score

        total = len(df)
        passers = df['Passed'].sum()
        failed = total - passers
        pct = (passers/total)*100

        # Build output table
        result = pd.DataFrame({
            'Subjects Taken':['Filipino 6'],
            'Number of Takers':[total],
            'Number of Passers':[passers],
            'Number of Failed':[failed],
            'Percentage Passing':[round(pct,2)]
        })

        st.subheader("📈 Summary Results")
        st.dataframe(result)

        # download
        file='summary.xlsx'
        result.to_excel(file, index=False, engine='openpyxl')

        with open(file,'rb') as f:
            st.download_button("⬇️ Download Excel", f, file_name='summary.xlsx')

        st.success("Analysis complete ✅")
