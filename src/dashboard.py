
from pathlib import Path
import subprocess
import sys

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "output"

st.set_page_config(
    page_title="RetailPulse",
    page_icon="📊",
    layout="wide"
)

st.title("RetailPulse")
st.caption("E-commerce performance overview")

needed = [
    "daily_sales.csv",
    "customer_summary.csv",
    "funnel_summary.csv"
]

# Generate data and run the pipeline if outputs are missing
if not all((OUT / file).exists() for file in needed):
    with st.spinner("Preparing RetailPulse analytics..."):
        try:
            subprocess.run(
                [sys.executable, str(ROOT / "src" / "generate_data.py")],
                cwd=ROOT,
                check=True
            )

            subprocess.run(
                [sys.executable, str(ROOT / "src" / "pipeline.py")],
                cwd=ROOT,
                check=True
            )

        except subprocess.CalledProcessError as error:
            st.error(f"Data preparation failed: {error}")
            st.stop()

if not all((OUT / file).exists() for file in needed):
    st.error("The analytics output files could not be created.")
    st.stop()

sales = pd.read_csv(OUT / needed[0], parse_dates=["day"])
customers = pd.read_csv(OUT / needed[1])
funnel = pd.read_csv(OUT / needed[2])

total_revenue = sales["revenue"].sum()
total_orders = sales["orders"].sum()

a, b, c = st.columns(3)

a.metric("Revenue", f"£{total_revenue:,.2f}")
b.metric("Orders", f"{int(total_orders):,}")
c.metric(
    "Average order value",
    f"£{total_revenue / max(total_orders, 1):,.2f}"
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
