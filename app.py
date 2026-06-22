import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from io import BytesIO

# ==================================
# PAGE CONFIGURATION
# ==================================
st.set_page_config(
    page_title="Assessment Summary",
    page_icon="📊",
    layout="wide"
)

# Hide Streamlit default menu/footer
st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

.metric-box {
    background-color: #f8f9fa;
    padding: 15px;
    border-radius: 12px;
    text-align: center;
    box-shadow: 0 2px 6px rgba(0,0,0,0.1);
}

.footer {
    text-align:center;
    color: gray;
    font-size: 14px;
}
</style>
""", unsafe_allow_html=True)

# ==================================
# HEADER
# ==================================
st.image("logo.gif", use_container_width=True)

st.markdown(
    """
    <div style='text-align:center'>
        <h1>📊 Pretest/Posttest Summarizer</h1>
        <p style='font-size:18px;color:gray'>
        Upload Excel files and automatically generate consolidated reports,
        summary tables, and visual analytics using a 75% passing rate.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

st.info(
    "📌 Upload one or more Excel files. "
    "The application will combine all datasets and compute summaries."
)



# ==================================
# SESSION STATE INIT
# ==================================
if "clear_uploader" not in st.session_state:
    st.session_state.clear_uploader = False

# ==================================
# FILE UPLOAD
# ==================================
uploaded_files = st.file_uploader(
    "Upload Excel Files",
    type=["xlsx"],
    accept_multiple_files=True,
    key=f"uploader_{st.session_state.clear_uploader}"
)

# ==================================
# CLEAR BUTTON
# ==================================
if st.button("Clear Uploaded Files"):
    st.session_state.clear_uploader = not st.session_state.clear_uploader
    st.rerun()

# ==================================
# PROCESSING
# ==================================
if uploaded_files:

    combined_df = pd.DataFrame()

    for file in uploaded_files:
        df = pd.read_excel(file, engine="openpyxl")
        df["Source_File"] = file.name
        combined_df = pd.concat([combined_df, df], ignore_index=True)

    st.subheader("📄 Combined Data Preview")
    st.dataframe(combined_df.head(), use_container_width=True)

    if "Total points" not in combined_df.columns:

        st.error("❌ Column 'Total points' not found.")

    else:

        max_score = combined_df["Total points"].max()
        passing_score = max_score * 0.75

        combined_df["Passed"] = (
            combined_df["Total points"] >= passing_score
        )

        summary = combined_df.groupby("Source_File").agg(
            Total_Takers=("Total points", "count"),
            Passers=("Passed", "sum")
        ).reset_index()

        summary["Failed"] = (
            summary["Total_Takers"] - summary["Passers"]
        )

        summary["Percentage Passing"] = (
            summary["Passers"] /
            summary["Total_Takers"] * 100
        )

        summary.rename(
            columns={"Source_File": "Subjects Taken"},
            inplace=True
        )

        # ==================================
        # KEY METRICS
        # ==================================
        total_students = summary["Total_Takers"].sum()
        total_pass = summary["Passers"].sum()
        total_fail = summary["Failed"].sum()
        overall_rate = (total_pass / total_students) * 100

        st.subheader("📌 Overall Statistics")

        c1, c2, c3, c4 = st.columns(4)

        c1.metric("Total Takers", f"{total_students:,}")
        c2.metric("Passers", f"{total_pass:,}")
        c3.metric("Failed", f"{total_fail:,}")
        c4.metric("Passing Rate", f"{overall_rate:.1f}%")

        # ==================================
        # SUMMARY TABLE
        # ==================================
        st.subheader("📈 Summary Results")

        display_summary = summary.copy()

        display_summary["Percentage Passing"] = (
            display_summary["Percentage Passing"]
            .round(2)
            .astype(str) + "%"
        )

        st.dataframe(
            display_summary,
            use_container_width=True,
            hide_index=True
        )

        # ==================================
        # VISUAL ANALYTICS
        # ==================================
        st.subheader("📊 Visual Analysis")

        col1, col2 = st.columns(2)

        # Pass vs Fail
        with col1:
            fig1, ax1 = plt.subplots(figsize=(7, 4))

            summary.set_index(
                "Subjects Taken"
            )[["Passers", "Failed"]].plot(
                kind="bar",
                ax=ax1,
                color=["#2E8B57", "#DC3545"]
            )

            ax1.set_title("Passers vs Failed")
            ax1.set_ylabel("Number of Students")
            ax1.set_xlabel("")

            plt.xticks(rotation=45)

            st.pyplot(fig1)

        # Passing Rate
        with col2:
            fig2, ax2 = plt.subplots(figsize=(7, 4))

            summary.set_index(
                "Subjects Taken"
            )["Percentage Passing"].plot(
                kind="bar",
                ax=ax2,
                color="#0D6EFD"
            )

            ax2.set_title("Passing Rate (%)")
            ax2.set_ylabel("Percentage")

            plt.xticks(rotation=45)

            st.pyplot(fig2)

        # Pie Chart
        st.markdown("### Overall Passing Distribution")

        fig3, ax3 = plt.subplots(figsize=(6, 6))

        ax3.pie(
            [total_pass, total_fail],
            labels=["Pass", "Fail"],
            autopct="%1.1f%%",
            startangle=90,
            colors=["#2E8B57", "#DC3545"],
            explode=(0.03, 0)
        )

        ax3.set_title("Overall Pass vs Fail")

        st.pyplot(fig3)

        # ==================================
        # DOWNLOAD
        # ==================================
        output = BytesIO()

        with pd.ExcelWriter(
            output,
            engine="openpyxl"
        ) as writer:
            summary.to_excel(
                writer,
                index=False,
                sheet_name="Summary"
            )

        st.download_button(
            "⬇️ Download Excel Summary",
            data=output.getvalue(),
            file_name="Assessment_Summary.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        st.success("✅ Analysis completed successfully.")

# =============================
# FOOTER
# =============================

from datetime import datetime

st.divider()

col_pic, col_text = st.columns([1, 6])

with col_pic:
    st.image("samson.jpg", width=80)

with col_text:
    st.markdown(
        f"""
        **Developed by Sir Sam**   
        Project PP Summarizer • SDO Masbate City  
        © {datetime.now().year} . All rights reserved.
        """
    )
