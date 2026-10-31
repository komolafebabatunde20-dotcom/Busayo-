# ============================================================
# GOVERNMENT BUDGET ALLOCATION AND EXPENDITURE MONITORING
# SYSTEM
# ============================================================

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import io

# ============================================================
# 1. PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Government Budget Monitoring System",
    page_icon="🏛️",
    layout="wide"
)

st.title("🏛️ GOVERNMENT BUDGET MONITORING SYSTEM")
st.write(
    "A Python-based system for monitoring government "
    "budget allocations and expenditures."
)

st.caption("Demonstration application — sample records are simulated.")

# ============================================================
# 2. SAMPLE GOVERNMENT DATA
# ============================================================

sample_data = {
    "Ministry": [
        "Ministry of Education",
        "Ministry of Health",
        "Ministry of Works",
        "Ministry of Agriculture",
        "Ministry of Finance",
        "Ministry of Transport",
        "Ministry of Environment"
    ],

    "Budget_Allocation": [
        500000000,
        400000000,
        600000000,
        300000000,
        250000000,
        350000000,
        200000000
    ],

    "Expenditure": [
        350000000,
        420000000,
        450000000,
        150000000,
        200000000,
        280000000,
        100000000
    ],

    "Financial_Year": [
        2026, 2026, 2026, 2026, 2026, 2026, 2026
    ]
}

sample_df = pd.DataFrame(sample_data)

# ============================================================
# 3. DATA INPUT
# ============================================================

st.sidebar.header("Data Management")

data_option = st.sidebar.radio(
    "Select Data Source",
    ["Use Sample Data", "Upload Government CSV"]
)

if data_option == "Upload Government CSV":

    uploaded_file = st.sidebar.file_uploader(
        "Upload Budget CSV File",
        type=["csv"]
    )

    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
    else:
        st.info("Upload a CSV file to continue.")
        st.stop()

else:
    df = sample_df.copy()

# ============================================================
# 4. DATA VALIDATION
# ============================================================

required_columns = [
    "Ministry",
    "Budget_Allocation",
    "Expenditure",
    "Financial_Year"
]

missing_columns = [
    col for col in required_columns if col not in df.columns
]

if missing_columns:
    st.error(f"Missing columns: {missing_columns}")
    st.stop()

if df.empty:
    st.error("The uploaded dataset is empty.")
    st.stop()

df["Budget_Allocation"] = pd.to_numeric(
    df["Budget_Allocation"], errors="coerce"
)

df["Expenditure"] = pd.to_numeric(
    df["Expenditure"], errors="coerce"
)

df["Financial_Year"] = pd.to_numeric(
    df["Financial_Year"], errors="coerce"
)

df = df.dropna(subset=[
    "Ministry",
    "Budget_Allocation",
    "Expenditure",
    "Financial_Year"
]).copy()

if df.empty:
    st.error("No valid records remain after data validation.")
    st.stop()

if (
    (df["Budget_Allocation"] < 0).any()
    or (df["Expenditure"] < 0).any()
):
    st.error("Budget and expenditure values cannot be negative.")
    st.stop()

# ============================================================
# 5. BUDGET ANALYSIS
# ============================================================

df["Remaining_Budget"] = (
    df["Budget_Allocation"] - df["Expenditure"]
)

df["Utilization_Percentage"] = np.where(
    df["Budget_Allocation"] > 0,
    (df["Expenditure"] / df["Budget_Allocation"]) * 100,
    np.nan
)

df["Budget_Status"] = np.where(
    df["Expenditure"] > df["Budget_Allocation"],
    "Overspending",
    np.where(
        df["Expenditure"] == df["Budget_Allocation"],
        "Fully Utilized",
        "Within Budget"
    )
)

# ============================================================
# 6. FINANCIAL YEAR FILTER
# ============================================================

st.sidebar.subheader("Filter Records")

years = sorted(
    df["Financial_Year"].astype(int).unique().tolist()
)

selected_year = st.sidebar.selectbox(
    "Select Financial Year",
    years
)

filtered_df = df[
    df["Financial_Year"] == selected_year
].copy()

if filtered_df.empty:
    st.warning("No records found for this financial year.")
    st.stop()

# ============================================================
# 7. KEY FINANCIAL INDICATORS
# ============================================================

total_budget = filtered_df["Budget_Allocation"].sum()

total_expenditure = filtered_df["Expenditure"].sum()

total_balance = total_budget - total_expenditure

if total_budget > 0:
    overall_utilization = (
        total_expenditure / total_budget
    ) * 100
else:
    overall_utilization = 0

overspending_count = (
    filtered_df["Budget_Status"] == "Overspending"
).sum()

st.subheader(f"Financial Overview: {selected_year}")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total Budget",
    f"₦{total_budget:,.0f}"
)

col2.metric(
    "Total Expenditure",
    f"₦{total_expenditure:,.0f}"
)

col3.metric(
    "Remaining Budget",
    f"₦{total_balance:,.0f}"
)

col4.metric(
    "Budget Utilization",
    f"{overall_utilization:.2f}%"
)

st.metric(
    "Departments Overspending",
    int(overspending_count)
)

# ============================================================
# 8. GOVERNMENT FINANCIAL RECORDS
# ============================================================

st.subheader("Government Budget Records")

st.dataframe(
    filtered_df,
    use_container_width=True,
    hide_index=True
)

# ============================================================
# 9. BUDGET UTILIZATION CHART
# ============================================================

st.subheader("Budget Allocation vs Expenditure")

fig, ax = plt.subplots(figsize=(11, 5))

x = np.arange(len(filtered_df))
width = 0.35

ax.bar(
    x - width / 2,
    filtered_df["Budget_Allocation"],
    width,
    label="Budget Allocation"
)

ax.bar(
    x + width / 2,
    filtered_df["Expenditure"],
    width,
    label="Actual Expenditure"
)

ax.set_xticks(x)
ax.set_xticklabels(
    filtered_df["Ministry"],
    rotation=35,
    ha="right"
)

ax.set_ylabel("Amount (Naira)")
ax.set_title("Government Budget Performance")
ax.legend()

plt.tight_layout()
st.pyplot(fig)
plt.close(fig)

# ============================================================
# 10. BUDGET UTILIZATION ANALYSIS
# ============================================================

st.subheader("Departmental Budget Utilization")

fig2, ax2 = plt.subplots(figsize=(10, 5))

ax2.barh(
    filtered_df["Ministry"],
    filtered_df["Utilization_Percentage"]
)

ax2.set_xlabel("Utilization Percentage (%)")
ax2.set_title("Budget Utilization by Ministry")

plt.tight_layout()
st.pyplot(fig2)
plt.close(fig2)

# ============================================================
# 11. OVERSPENDING DETECTION
# ============================================================

st.subheader("⚠️ Overspending Detection")

overspending_df = filtered_df[
    filtered_df["Budget_Status"] == "Overspending"
]

if not overspending_df.empty:

    st.error(
        f"{len(overspending_df)} department(s) "
        "have exceeded their budget allocation."
    )

    st.dataframe(
        overspending_df[
            [
                "Ministry",
                "Budget_Allocation",
                "Expenditure",
                "Remaining_Budget",
                "Budget_Status"
            ]
        ],
        use_container_width=True,
        hide_index=True
    )

else:

    st.success(
        "No overspending detected in the selected financial year."
    )

# ============================================================
# 12. UNDERUTILIZATION DETECTION
# ============================================================

st.subheader("Underutilized Budget")

underutilized_df = filtered_df[
    (filtered_df["Budget_Allocation"] > 0)
    & (filtered_df["Utilization_Percentage"] < 40)
]

if not underutilized_df.empty:

    st.warning(
        f"{len(underutilized_df)} department(s) "
        "have utilized less than 40% of their allocation."
    )

    st.dataframe(
        underutilized_df[
            [
                "Ministry",
                "Budget_Allocation",
                "Expenditure",
                "Utilization_Percentage"
            ]
        ],
        use_container_width=True,
        hide_index=True
    )

else:

    st.success("No department is below the 40% utilization threshold.")

# ============================================================
# 13. MINISTRY SEARCH
# ============================================================

st.subheader("Search Government Ministry")

search = st.text_input(
    "Enter Ministry Name"
)

if search:

    search_result = filtered_df[
        filtered_df["Ministry"].str.contains(
            search,
            case=False,
            na=False
        )
    ]

    st.dataframe(
        search_result,
        use_container_width=True,
        hide_index=True
    )

# ============================================================
# 14. DOWNLOAD GOVERNMENT REPORT
# ============================================================

st.subheader("Download Financial Report")

csv_data = filtered_df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download Budget Analysis CSV",
    data=csv_data,
    file_name=f"government_budget_report_{selected_year}.csv",
    mime="text/csv"
)

# ============================================================
# 15. SYSTEM SUMMARY
# ============================================================

st.subheader("Financial Analysis Summary")

st.write(f"Financial Year: {selected_year}")

st.write(f"Number of Ministries: {len(filtered_df)}")

st.write(f"Total Budget: ₦{total_budget:,.2f}")

st.write(f"Total Expenditure: ₦{total_expenditure:,.2f}")

st.write(f"Total Remaining Budget: ₦{total_balance:,.2f}")

st.write(
    f"Overall Budget Utilization: {overall_utilization:.2f}%"
)

st.write(
    f"Number of Overspending Ministries: {overspending_count}"
)

st.caption(
    "Government Budget Monitoring System | "
    "Python Public Administration Project"
)

st.success("Budget analysis completed successfully!")
