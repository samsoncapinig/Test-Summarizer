
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Advanced LMS Dashboard", layout="wide")

st.title("📊 Pretest vs Posttest Dashboard with Gain Analysis")

st.info("Upload Pretest and Posttest Excel files (multiple allowed). Uses 75% passing rate.")

uploaded_files = st.file_uploader("Upload Excel Files", type=['xlsx'], accept_multiple_files=True)

if uploaded_files:
    all_data = []

    for file in uploaded_files:
        df = pd.read_excel(file, engine='openpyxl')
        df['File'] = file.name.lower()

        # Identify test type
        if 'pre' in file.name.lower():
            df['Test'] = 'Pretest'
        elif 'post' in file.name.lower():
            df['Test'] = 'Posttest'
        else:
            df['Test'] = 'Unknown'

        all_data.append(df)

    data = pd.concat(all_data, ignore_index=True)

    if 'Total points' not in data.columns:
        st.error("Missing 'Total points' column.")
    else:
        max_score = data['Total points'].max()
        passing = max_score * 0.75

        data['Passed'] = data['Total points'] >= passing

        summary = data.groupby('Test').agg(
            Takers=('Total points','count'),
            Passers=('Passed','sum')
        ).reset_index()

        summary['Failed'] = summary['Takers'] -
summary['Passers']
        summary['Passing %'] = (summary['Passers']/summary['Takers'])*100

        st.subheader("📈 Summary Table")
        st.dataframe(summary)

        # Gain Analysis
        if set(summary['Test']) >= {'Pretest','Posttest'}:
            pre = summary[summary['Test']=='Pretest']['Passing %'].values[0]
            post = summary[summary['Test']=='Posttest']['Passing %'].values[0]
            gain = post - pre

            st.subheader("📊 Gain Analysis")
            st.metric("Pretest Passing %", f"{pre:.2f}%")
            st.metric("Posttest Passing %", f"{post:.2f}%")
            st.metric("Gain (%)", f"{gain:.2f}")

        # Chart
        st.subheader("📉 Comparison Chart")
        fig, ax = plt.subplots()
        ax.bar(summary['Test'], summary['Passing %'])
        ax.set_ylabel("Passing Percentage")
        ax.set_title("Pretest vs Posttest Performance")

        st.pyplot(fig)

        # Export
        output='advanced_summary.xlsx'
        summary.to_excel(output, index=False, engine='openpyxl')

        with open(output,'rb') as f:
            st.download_button("⬇️ Download Report", f, file_name=output)

        st.success("Analysis Complete ✅")
