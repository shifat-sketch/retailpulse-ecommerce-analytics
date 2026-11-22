
from pathlib import Path
import pandas as pd
import streamlit as st
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "output"

st.set_page_config(page_title="RetailPulse", page_icon="📊", layout="wide")

st.title("RetailPulse")
st.caption("E-commerce performance overview")

needed = [
    "daily_sales.csv",
    "customer_summary.csv",
    "funnel_summary.csv"
]

# Generate data and run the pipeline if output files are missing
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

a, b, c = st.columns(3)

a.metric("Revenue", f"£{sales.revenue.sum():,.2f}")
b.metric("Orders", f"{int(sales.orders.sum()):,}")
c.metric(
    "Average order value",
    f"£{sales.revenue.sum() / max(sales.orders.sum(), 1):,.2f}"
)

st.subheader("Daily revenue")
st.line_chart(sales.set_index("day")["revenue"], width="stretch")

left, right = st.columns(2)

left.subheader("Top customers")
left.dataframe(customers.head(15), width="stretch")

right.subheader("Event funnel")
right.bar_chart(
    funnel.set_index("event_type")["event_count"],
    width="stretch"
)
right.dataframe(funnel, width="stretch")
