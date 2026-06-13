import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from io import BytesIO
import plotly.express as px
import plotly.graph_objects as go

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
# FILE UPLOAD
# ==================================
uploaded_files = st.file_uploader(
    "Upload Excel Files",
    type=["xlsx"],
    accept_multiple_files=True
)

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
        # VISUAL ANALYTICS (PLOTLY)
        # ==================================
        st.subheader("📊 Visual Analysis")
        
        col1, col2 = st.columns(2)
        
        # ==================================
        # PASSERS VS FAILED
        # ==================================
        with col1:
        
            pass_fail_df = summary.melt(
                id_vars="Subjects Taken",
                value_vars=["Passers", "Failed"],
                var_name="Status",
                value_name="Students"
            )
        
            fig1 = px.bar(
                pass_fail_df,
                x="Subjects Taken",
                y="Students",
                color="Status",
                barmode="group",
                title="Passers vs Failed per Subject",
                text="Students",
                color_discrete_map={
                    "Passers": "#2E8B57",
                    "Failed": "#DC3545"
                }
            )
        
            fig1.update_traces(textposition="outside")
        
            fig1.update_layout(
                xaxis_title="Subjects",
                yaxis_title="Number of Students",
                legend_title="",
                height=450,
                hovermode="x unified"
            )
        
            st.plotly_chart(fig1, use_container_width=True)
        
        
        # ==================================
        # PASSING RATE
        # ==================================
        with col2:
        
            fig2 = px.bar(
                summary,
                x="Subjects Taken",
                y="Percentage Passing",
                title="Passing Rate (%) per Subject",
                text=summary["Percentage Passing"].round(1).astype(str) + "%",
                color="Percentage Passing",
                color_continuous_scale="Blues"
            )
        
            fig2.update_traces(textposition="outside")
        
            fig2.update_layout(
                xaxis_title="Subjects",
                yaxis_title="Passing Rate (%)",
                coloraxis_showscale=False,
                height=450
            )
        
            st.plotly_chart(fig2, use_container_width=True)
        
        
        # ==================================
        # OVERALL PASS VS FAIL PIE CHART
        # ==================================
        st.markdown("### Overall Passing Distribution")
        
        fig3 = go.Figure(
            data=[
                go.Pie(
                    labels=["Pass", "Fail"],
                    values=[total_pass, total_fail],
                    hole=0.45,
                    textinfo="label+percent+value",
                    marker=dict(
                        colors=["#2E8B57", "#DC3545"]
                    ),
                    pull=[0.03, 0]
                )
            ]
        )
        
        fig3.update_layout(
            title="Overall Pass vs Fail Distribution",
            height=500,
            showlegend=True
        )
        
        st.plotly_chart(fig3, use_container_width=True)
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

# ==================================
# FOOTER
# ==================================
st.divider()

col1, col2, col3 = st.columns([1, 5, 1])

with col2:
    st.image("samson.png", width=90)

    st.markdown(
        f"""
        <div class='footer'>
            <strong>Developed by Sir Sam</strong><br>
            Pretest/Posttest Summarizer • SDO Masbate City<br>
            © {datetime.now().year} All Rights Reserved
        </div>
        """,
        unsafe_allow_html=True
    )
