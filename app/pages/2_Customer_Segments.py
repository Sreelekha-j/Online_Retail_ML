"""
Page 2: Customer Segments
Shows the 4 customer groups I found with K-Means clustering in Phase 3.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from utils import load_rfm, apply_style

st.set_page_config(page_title="Customer Segments", page_icon="👥", layout="wide")
apply_style()

rfm = load_rfm()

ORDER = ['Champions', 'New Customers', 'At Risk', 'Lost Customers']
COLORS = {'Champions': '#10B981', 'New Customers': '#0EA5E9',
          'At Risk': '#F59E0B', 'Lost Customers': '#EF4444'}
ACTIONS = {
    'Champions': "Reward them with loyalty perks and early access to new products. Keep them happy.",
    'New Customers': "Welcome them and encourage a second order, for example with a small discount.",
    'At Risk': "Contact them soon with a personal offer, before they are lost.",
    'Lost Customers': "Try a low-cost win-back email, but don't spend much budget on this group.",
}

st.title("👥 Customer Segments")
st.caption("Customer groups found with K-Means clustering on Recency, Frequency and Monetary (Phase 3).")

# ---------- Profile of each cluster ----------
profile = rfm.groupby('ClusterName').agg(
    Customers=('Customer ID', 'count'),
    Median_Recency=('Recency', 'median'),
    Median_Frequency=('Frequency', 'median'),
    Median_Monetary=('Monetary', 'median'),
    Revenue=('Monetary', 'sum'),
).reindex(ORDER)
profile['Customer_Share'] = profile['Customers'] / profile['Customers'].sum() * 100
profile['Revenue_Share'] = profile['Revenue'] / profile['Revenue'].sum() * 100

# ---------- KPI cards ----------
k1, k2, k3, k4 = st.columns(4)
k1.metric("Customers", f"{len(rfm):,}")
k2.metric("Champions share", f"{profile.loc['Champions', 'Customer_Share']:.1f}%")
k3.metric("Champions revenue", f"{profile.loc['Champions', 'Revenue_Share']:.1f}%")
k4.metric("Lost customers", f"{int(profile.loc['Lost Customers', 'Customers']):,}")

chart_layout = dict(plot_bgcolor="white", paper_bgcolor="white",
                    margin=dict(l=10, r=10, t=10, b=10), height=350)

# ---------- Row 1: customers and revenue per cluster ----------
col1, col2 = st.columns(2)

with col1:
    with st.container(border=True):
        st.subheader("Customers in each group")
        fig = px.pie(profile.reset_index(), names='ClusterName', values='Customers', hole=0.5,
                     color='ClusterName', color_discrete_map=COLORS)
        fig.update_layout(**chart_layout)
        st.plotly_chart(fig, use_container_width=True)

with col2:
    with st.container(border=True):
        st.subheader("Share of revenue")
        fig = px.bar(profile.reset_index(), x='ClusterName', y='Revenue_Share',
                     color='ClusterName', color_discrete_map=COLORS,
                     text=profile['Revenue_Share'].round(1).astype(str) + '%')
        fig.update_layout(**chart_layout, showlegend=False,
                          xaxis_title='', yaxis_title='Revenue share (%)')
        st.plotly_chart(fig, use_container_width=True)

# ---------- Profile table ----------
with st.container(border=True):
    st.subheader("What a typical customer in each group looks like")
    table = profile[['Customers', 'Median_Recency', 'Median_Frequency',
                     'Median_Monetary', 'Revenue_Share']].reset_index()
    st.dataframe(
        table, hide_index=True, use_container_width=True,
        column_config={
            'ClusterName': 'Group',
            'Median_Recency': st.column_config.NumberColumn('Days since last order', format="%.0f"),
            'Median_Frequency': st.column_config.NumberColumn('Orders', format="%.0f"),
            'Median_Monetary': st.column_config.NumberColumn('Spend', format="£%.0f"),
            'Revenue_Share': st.column_config.NumberColumn('Revenue share', format="%.1f%%"),
        },
    )

# ---------- Row 2: scatter and comparison with RFM segments ----------
col3, col4 = st.columns(2)

with col3:
    with st.container(border=True):
        st.subheader("Recency vs spend")
        fig = px.scatter(rfm, x='Recency', y='Monetary', color='ClusterName',
                         color_discrete_map=COLORS, category_orders={'ClusterName': ORDER},
                         log_y=True, opacity=0.6,
                         hover_data={'Customer ID': True, 'Frequency': True})
        fig.update_layout(**chart_layout, legend_title_text='',
                          xaxis_title='Days since last order', yaxis_title='Total spend (£, log scale)')
        st.plotly_chart(fig, use_container_width=True)

with col4:
    with st.container(border=True):
        st.subheader("Clusters vs my RFM segments (%)")
        ct = pd.crosstab(rfm['Segment'], rfm['ClusterName'], normalize='index') * 100
        ct = ct.reindex(columns=ORDER)
        fig = px.imshow(ct.round(0), text_auto=True, color_continuous_scale='Blues', aspect='auto')
        fig.update_layout(**chart_layout, xaxis_title='K-Means cluster',
                          yaxis_title='RFM segment', coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

# ---------- Customer lookup ----------
with st.container(border=True):
    st.subheader("🔍 Look up a customer")
    customer = st.selectbox("Choose a Customer ID", rfm['Customer ID'].sort_values(),
                            format_func=lambda x: str(int(x)))
    row = rfm[rfm['Customer ID'] == customer].iloc[0]
    group = row['ClusterName']

    c1, c2, c3, c4 = st.columns([1.6, 1, 1, 1])
    c1.metric("Group", group)
    c2.metric("Days since last order", f"{int(row['Recency'])}")
    c3.metric("Orders", f"{int(row['Frequency'])}")
    c4.metric("Total spend", f"£{row['Monetary']:,.0f}")

    st.info(f"**Suggested action:** {ACTIONS[group]}")
    st.caption(f"In my rule-based RFM segments (Phase 1), this customer is: {row['Segment']}")