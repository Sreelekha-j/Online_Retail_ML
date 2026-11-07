import streamlit as st
from utils import load_sales, apply_style  

st.set_page_config(page_title="Retail Customer Analytics", page_icon="🛒", layout="wide")
apply_style()                                 
st.title("🛒 Online Retail: Customer Analytics and Churn Prediction")

st.write(
    "This app is based on my project using the Online Retail II dataset "
    "(a UK online gift shop, December 2009 to December 2011)."
)

st.markdown("""
### What you can find in this app
- **Sales Dashboard:** sales trends, top countries and top products
- **Customer Segments:** customer groups found with K-Means clustering
- **Churn Predictor:** the churn risk of each customer, using my final XGBoost model
- **Model Comparison:** how all my models performed and which features matter most

Use the menu on the left to open a page.
""")

sales = load_sales()

st.markdown("### The data at a glance")
col1, col2, col3 = st.columns(3)
col1.metric("Total revenue", f"£{sales['Revenue'].sum():,.0f}")
col2.metric("Customers", f"{sales['Customer ID'].nunique():,}")
col3.metric("Orders", f"{sales['Invoice'].nunique():,}")