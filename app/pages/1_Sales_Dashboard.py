"""
Page 1: Sales Dashboard
Interactive version of my Phase 1 sales analysis, with filters for date and country.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from utils import load_sales, apply_style

st.set_page_config(page_title="Sales Dashboard", page_icon="📊", layout="wide")
apply_style()

ACCENT = "#4F46E5"
sales = load_sales()

st.title("📊 Sales Dashboard")
st.caption("Use the filters on the left. All numbers and charts update automatically.")

# ---------- Sidebar filters ----------
st.sidebar.header("Filters")

min_date = sales['InvoiceDate'].min().date()
max_date = sales['InvoiceDate'].max().date()
date_range = st.sidebar.date_input("Date range", value=(min_date, max_date),
                                   min_value=min_date, max_value=max_date)

countries = sorted(sales['Country'].unique())
selected_countries = st.sidebar.multiselect("Country", countries,
                                            placeholder="All countries")

# Apply the filters
if len(date_range) == 2:
    start, end = date_range
else:
    start, end = min_date, max_date

mask = (sales['InvoiceDate'].dt.date >= start) & (sales['InvoiceDate'].dt.date <= end)
if selected_countries:
    mask = mask & sales['Country'].isin(selected_countries)
df = sales[mask]

if df.empty:
    st.warning("No sales for these filters. Try a wider date range or other countries.")
    st.stop()

# ---------- KPI cards ----------
revenue = df['Revenue'].sum()
orders = df['Invoice'].nunique()
customers = df['Customer ID'].nunique()

k1, k2, k3, k4 = st.columns(4)
k1.metric("Revenue", f"£{revenue:,.0f}")
k2.metric("Orders", f"{orders:,}")
k3.metric("Customers", f"{customers:,}")
k4.metric("Avg order value", f"£{revenue / orders:,.0f}")


def style_chart(fig):
    """Same clean look for every chart."""
    fig.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                      margin=dict(l=10, r=10, t=10, b=10), height=350)
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(gridcolor="#EEF0F4")
    return fig


# ---------- Row 1: monthly revenue ----------
with st.container(border=True):
    st.subheader("Monthly revenue")
    monthly = (df.groupby(df['InvoiceDate'].dt.to_period('M').dt.to_timestamp())['Revenue']
                 .sum().reset_index())
    monthly.columns = ['Month', 'Revenue']
    fig = px.line(monthly, x='Month', y='Revenue', markers=True,
                  color_discrete_sequence=[ACCENT])
    fig.update_traces(hovertemplate="%{x|%b %Y}<br>£%{y:,.0f}")
    st.plotly_chart(style_chart(fig), use_container_width=True)
    st.caption("Note: December 2011 only has data until the 9th, so the last point is lower.")

# ---------- Row 2: top countries and top products ----------
col1, col2 = st.columns(2)

with col1:
    with st.container(border=True):
        st.subheader("Top 10 countries")
        top_countries = df.groupby('Country')['Revenue'].sum().nlargest(10).reset_index()
        fig = px.bar(top_countries, x='Revenue', y='Country', orientation='h',
                     color_discrete_sequence=[ACCENT])
        fig.update_layout(yaxis={'categoryorder': 'total ascending'})
        fig.update_traces(hovertemplate="%{y}<br>£%{x:,.0f}")
        st.plotly_chart(style_chart(fig), use_container_width=True)

with col2:
    with st.container(border=True):
        st.subheader("Top 10 products")
        top_products = df.groupby('Description')['Revenue'].sum().nlargest(10).reset_index()
        fig = px.bar(top_products, x='Revenue', y='Description', orientation='h',
                     color_discrete_sequence=["#0EA5E9"])
        fig.update_layout(yaxis={'categoryorder': 'total ascending', 'title': ''})
        fig.update_traces(hovertemplate="%{y}<br>£%{x:,.0f}")
        st.plotly_chart(style_chart(fig), use_container_width=True)

# ---------- Row 3: when do customers buy ----------
col3, col4 = st.columns(2)

with col3:
    with st.container(border=True):
        st.subheader("Revenue by day of the week")
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        by_day = df.groupby(df['InvoiceDate'].dt.day_name())['Revenue'].sum().reset_index()
        by_day.columns = ['Day', 'Revenue']
        fig = px.bar(by_day, x='Day', y='Revenue', category_orders={'Day': day_order},
                     color_discrete_sequence=["#10B981"])
        fig.update_traces(hovertemplate="%{x}<br>£%{y:,.0f}")
        st.plotly_chart(style_chart(fig), use_container_width=True)

with col4:
    with st.container(border=True):
        st.subheader("Revenue by hour of the day")
        by_hour = df.groupby(df['InvoiceDate'].dt.hour)['Revenue'].sum().reset_index()
        by_hour.columns = ['Hour', 'Revenue']
        fig = px.bar(by_hour, x='Hour', y='Revenue', color_discrete_sequence=["#F59E0B"])
        fig.update_traces(hovertemplate="%{x}:00<br>£%{y:,.0f}")
        st.plotly_chart(style_chart(fig), use_container_width=True)