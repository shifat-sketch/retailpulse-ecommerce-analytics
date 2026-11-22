
from pathlib import Path
import pandas as pd
import streamlit as st
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "output"

st.set_page_config(
    page_title="RetailPulse",
    page_icon="📊",
    layout="wide"
)

st.title("RetailPulse")
st.caption("E-commerce Analytics & Business Intelligence Dashboard")

needed = [
    "daily_sales.csv",
    "customer_summary.csv",
    "funnel_summary.csv"
]

# Prepare data if output files are missing
if not all((OUT / x).exists() for x in needed):
    with st.spinner("Preparing RetailPulse data..."):
        subprocess.run(
            [sys.executable, str(ROOT / "src" / "generate_data.py")],
            check=True
        )
        subprocess.run(
            [sys.executable, str(ROOT / "src" / "pipeline.py")],
            check=True
        )

sales = pd.read_csv(OUT / needed[0], parse_dates=["day"])
customers = pd.read_csv(OUT / needed[1])
funnel = pd.read_csv(OUT / needed[2])

sales["day"] = pd.to_datetime(sales["day"])
sales = sales.sort_values("day")

# Sidebar filters
st.sidebar.header("Dashboard Filters")

min_date = sales["day"].min().date()
max_date = sales["day"].max().date()

date_range = st.sidebar.date_input(
    "Select date range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

if len(date_range) == 2:
    start_date, end_date = date_range
    filtered_sales = sales[
        (sales["day"].dt.date >= start_date) &
        (sales["day"].dt.date <= end_date)
    ]
else:
    filtered_sales = sales

# Key performance indicators
total_revenue = filtered_sales["revenue"].sum()
total_orders = filtered_sales["orders"].sum()
average_order = total_revenue / max(total_orders, 1)

st.subheader("Key Performance Indicators")

a, b, c = st.columns(3)

a.metric("Total Revenue", f"£{total_revenue:,.2f}")
b.metric("Total Orders", f"{int(total_orders):,}")
c.metric("Average Order Value", f"£{average_order:,.2f}")

st.divider()

# Daily revenue analysis
st.subheader("Daily Revenue Trend")

if not filtered_sales.empty:
    st.line_chart(
        filtered_sales.set_index("day")["revenue"],
        width="stretch"
    )
else:
    st.info("No sales data available for this date range.")

# Monthly revenue analysis
st.subheader("Monthly Revenue Analysis")

if not filtered_sales.empty:
    monthly_sales = (
        filtered_sales
        .set_index("day")
        .resample("ME")["revenue"]
        .sum()
    )

    st.bar_chart(monthly_sales, width="stretch")
else:
    st.info("No monthly revenue data available.")

st.divider()

# Customer and funnel analysis
left, right = st.columns(2)

left.subheader("Top Customers")
left.dataframe(customers.head(15), width="stretch")

right.subheader("Event Funnel")
right.bar_chart(
    funnel.set_index("event_type")["event_count"],
    width="stretch"
)
right.dataframe(funnel, width="stretch")

st.divider()

# Business insights
st.subheader("Business Performance Insights")

if not filtered_sales.empty:
    best_day = filtered_sales.loc[
        filtered_sales["revenue"].idxmax()
    ]

    insight1, insight2 = st.columns(2)

    insight1.metric(
        "Highest Revenue Day",
        best_day["day"].strftime("%d %b %Y")
    )

    insight2.metric(
        "Highest Daily Revenue",
        f"£{best_day['revenue']:,.2f}"
    )

    st.write(
        f"During the selected period, the business generated "
        f"**£{total_revenue:,.2f}** in revenue from "
        f"**{int(total_orders):,} orders**."
    )
