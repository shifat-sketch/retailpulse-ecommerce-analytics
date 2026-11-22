from pathlib import Path
import pandas as pd
import streamlit as st

OUT=Path(__file__).resolve().parents[1]/"data"/"output"
st.set_page_config(page_title="RetailPulse",page_icon="📊",layout="wide")
st.title("RetailPulse")
st.caption("E-commerce performance overview")
needed=["daily_sales.csv","customer_summary.csv","funnel_summary.csv"]
if not all((OUT/x).exists() for x in needed):
    st.warning("Run the data generator and pipeline first: python src/generate_data.py && python src/pipeline.py")
    st.stop()
sales=pd.read_csv(OUT/needed[0],parse_dates=["day"])
customers=pd.read_csv(OUT/needed[1]); funnel=pd.read_csv(OUT/needed[2])
a,b,c=st.columns(3)
a.metric("Revenue",f"£{sales.revenue.sum():,.2f}")
b.metric("Orders",f"{int(sales.orders.sum()):,}")
c.metric("Average order value",f"£{sales.revenue.sum()/max(sales.orders.sum(),1):,.2f}")
st.subheader("Daily revenue"); st.line_chart(sales.set_index("day")["revenue"])
left,right=st.columns(2)
left.subheader("Top customers"); left.dataframe(customers.head(15),use_container_width=True)
right.subheader("Event funnel"); right.bar_chart(funnel.set_index("event_type")["event_count"]); right.dataframe(funnel,use_container_width=True)
