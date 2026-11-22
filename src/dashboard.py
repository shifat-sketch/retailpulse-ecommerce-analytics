
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
    "funnel_summary.csv",
    "product_summary.csv",
    "category_summary.csv",
    "retention_summary.csv"
]

# Prepare data if any output file is missing
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

# Load datasets
sales = pd.read_csv(OUT / "daily_sales.csv", parse_dates=["day"])
customers = pd.read_csv(OUT / "customer_summary.csv")
funnel = pd.read_csv(OUT / "funnel_summary.csv")
products = pd.read_csv(OUT / "product_summary.csv")
categories = pd.read_csv(OUT / "category_summary.csv")
retention = pd.read_csv(OUT / "retention_summary.csv")

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

# Main KPIs
total_revenue = filtered_sales["revenue"].sum()
total_orders = filtered_sales["orders"].sum()
average_order = total_revenue / max(total_orders, 1)

st.subheader("Key Performance Indicators")

a, b, c = st.columns(3)
a.metric("Total Revenue", f"£{total_revenue:,.2f}")
b.metric("Total Orders", f"{int(total_orders):,}")
c.metric("Average Order Value", f"£{average_order:,.2f}")

st.divider()

# Revenue trends
st.subheader("Daily Revenue Trend")

if not filtered_sales.empty:
    st.line_chart(
        filtered_sales.set_index("day")["revenue"],
        width="stretch"
    )
else:
    st.info("No sales data available for this date range.")

st.subheader("Monthly Revenue Analysis")

if not filtered_sales.empty:
    monthly_sales = (
        filtered_sales
        .set_index("day")
        .resample("ME")["revenue"]
        .sum()
    )
    st.bar_chart(monthly_sales, width="stretch")

st.divider()

# Product performance
st.header("Product Performance Analytics")

left, right = st.columns(2)

left.subheader("Top 10 Products by Revenue")
left.bar_chart(
    products.head(10).set_index("product_id")["revenue"],
    width="stretch"
)

right.subheader("Revenue by Category")
right.bar_chart(
    categories.set_index("category")["revenue"],
    width="stretch"
)

st.subheader("Product Performance Details")
st.dataframe(products.head(20), width="stretch")

st.divider()

# Customer retention
st.header("Customer Retention Analytics")

repeat = retention[
    retention["customer_segment"] == "Repeat customer"
]["customer_count"].sum()

one_time = retention[
    retention["customer_segment"] == "One-time customer"
]["customer_count"].sum()

no_purchase = retention[
    retention["customer_segment"] == "No purchase"
]["customer_count"].sum()

total_customers = repeat + one_time + no_purchase
repeat_rate = repeat / max(total_customers, 1) * 100

a, b, c = st.columns(3)
a.metric("Repeat Customers", f"{int(repeat):,}")
b.metric("One-time Customers", f"{int(one_time):,}")
c.metric("Repeat Customer Rate", f"{repeat_rate:.1f}%")

st.bar_chart(
    retention.set_index("customer_segment")["customer_count"],
    width="stretch"
)

st.dataframe(retention, width="stretch")

st.divider()

# Customer and event analysis
st.header("Customer & Conversion Analysis")

left, right = st.columns(2)

left.subheader("Top Customers")
left.dataframe(customers.head(15), width="stretch")

right.subheader("Customer Event Funnel")
right.bar_chart(
    funnel.set_index("event_type")["unique_customers"],
    width="stretch"
)
right.dataframe(funnel, width="stretch")

st.caption(
    "Funnel metrics represent unique customers by event type, "
    "not session-based conversion."
)

st.divider()

# Business insights
st.header("Business Performance Insights")

if not filtered_sales.empty:
    best_day = filtered_sales.loc[
        filtered_sales["revenue"].idxmax()
    ]

    best_category = categories.iloc[0]

    insight1, insight2, insight3 = st.columns(3)

    insight1.metric(
        "Highest Revenue Day",
        best_day["day"].strftime("%d %b %Y")
    )

    insight2.metric(
        "Highest Daily Revenue",
        f"£{best_day['revenue']:,.2f}"
    )

    insight3.metric(
        "Top Revenue Category",
        best_category["category"]
    )

    st.write(
        f"During the selected period, the business generated "
        f"**£{total_revenue:,.2f}** from "
        f"**{int(total_orders):,} orders**."
    )

    st.write(
        f"The highest-revenue product category is "
        f"**{best_category['category']}**, generating "
        f"**£{best_category['revenue']:,.2f}** overall."
    )
