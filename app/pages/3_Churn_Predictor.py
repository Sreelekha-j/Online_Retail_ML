"""
Page 3: Churn Predictor
Uses my final tuned XGBoost model (Phase 6) with a cut-off of 0.45
to predict which customers may not buy in the next 90 days.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils import load_churn_current, load_final_model, load_rfm, apply_style

st.set_page_config(page_title="Churn Predictor", page_icon="⚠️", layout="wide")
apply_style()

final = load_final_model()
model = final['model']
THRESHOLD = final['threshold']

RISK_COLORS = {'High': '#EF4444', 'Medium': '#F59E0B', 'Low': '#10B981'}
ORDER = ['Champions', 'New Customers', 'At Risk', 'Lost Customers']


@st.cache_data
def get_predictions():
    """Churn probability for every customer, plus their K-Means group."""
    current = load_churn_current().copy()
    X = current[model.feature_names_in_]          # same columns, same order as in training
    current['Churn_Probability'] = model.predict_proba(X)[:, 1]
    groups = load_rfm()[['Customer ID', 'ClusterName']]
    return current.merge(groups, on='Customer ID', how='left')


preds = get_predictions()
preds['Risk'] = pd.cut(preds['Churn_Probability'], bins=[-0.01, THRESHOLD, 0.7, 1.01],
                       labels=['Low', 'Medium', 'High'], right=False)

st.title("⚠️ Churn Predictor")
st.caption(f"Predicted risk that a customer will not buy in the next 90 days (after 9 Dec 2011). "
           f"Customers with a probability of {THRESHOLD} or more are predicted to churn.")

# ---------- Sidebar filter ----------
st.sidebar.header("Filters")
selected_groups = st.sidebar.multiselect("Customer group", ORDER, placeholder="All groups")
df = preds[preds['ClusterName'].isin(selected_groups)] if selected_groups else preds

at_risk = df[df['Churn_Probability'] >= THRESHOLD]

# ---------- KPI cards ----------
k1, k2, k3, k4 = st.columns(4)
k1.metric("Customers", f"{len(df):,}")
k2.metric("Predicted to churn", f"{len(at_risk):,} ({len(at_risk) / len(df) * 100:.0f}%)")
k3.metric("High risk (70%+)", f"{(df['Risk'] == 'High').sum():,}")
k4.metric("Past spend at risk", f"£{at_risk['Monetary'].sum():,.0f}")

chart_layout = dict(plot_bgcolor="white", paper_bgcolor="white",
                    margin=dict(l=10, r=10, t=10, b=10), height=350)

# ---------- Row 1: charts ----------
col1, col2 = st.columns(2)

with col1:
    with st.container(border=True):
        st.subheader("How churn risk is spread")
        fig = px.histogram(df, x='Churn_Probability', nbins=40, color='Risk',
                           color_discrete_map=RISK_COLORS,
                           category_orders={'Risk': ['High', 'Medium', 'Low']})
        fig.add_vline(x=THRESHOLD, line_dash='dash', line_color='black',
                      annotation_text=f"cut-off {THRESHOLD}")
        fig.update_layout(**chart_layout, xaxis_title='Churn probability',
                          yaxis_title='Customers', legend_title_text='Risk')
        st.plotly_chart(fig, use_container_width=True)

with col2:
    with st.container(border=True):
        st.subheader("Predicted churn by customer group")
        by_group = (df.groupby('ClusterName')['Churn_Probability']
                      .apply(lambda p: (p >= THRESHOLD).mean() * 100)
                      .reindex(ORDER).dropna().reset_index())
        by_group.columns = ['Group', 'Churn %']
        fig = px.bar(by_group, x='Group', y='Churn %', color='Group',
                     color_discrete_map={'Champions': '#10B981', 'New Customers': '#0EA5E9',
                                         'At Risk': '#F59E0B', 'Lost Customers': '#EF4444'},
                     text=by_group['Churn %'].round(0).astype(int).astype(str) + '%')
        fig.update_layout(**chart_layout, showlegend=False, xaxis_title='',
                          yaxis_title='% predicted to churn')
        st.plotly_chart(fig, use_container_width=True)

# ---------- At-risk customer list ----------
with st.container(border=True):
    st.subheader("📋 Customers to contact")
    st.caption("Customers predicted to churn, with the most valuable ones first.")

    table = at_risk.sort_values('Monetary', ascending=False).copy()
    table['Risk %'] = table['Churn_Probability'] * 100
    table = table[['Customer ID', 'ClusterName', 'Risk %', 'Recency', 'Frequency', 'Monetary']]

    st.dataframe(
        table, hide_index=True, use_container_width=True, height=350,
        column_config={
            'Customer ID': st.column_config.NumberColumn('Customer ID', format="%d"),
            'ClusterName': 'Group',
            'Risk %': st.column_config.ProgressColumn('Churn risk', format="%.0f%%",
                                                      min_value=0, max_value=100),
            'Recency': st.column_config.NumberColumn('Days since last order', format="%d"),
            'Frequency': st.column_config.NumberColumn('Orders', format="%d"),
            'Monetary': st.column_config.NumberColumn('Total spend', format="£%.0f"),
        },
    )
    st.download_button("⬇️ Download this list (CSV)", table.to_csv(index=False),
                       file_name="customers_at_risk.csv", mime="text/csv")

# ---------- Single customer check ----------
with st.container(border=True):
    st.subheader("🔍 Check one customer")
    customer = st.selectbox("Choose a Customer ID", preds['Customer ID'].sort_values(),
                            format_func=lambda x: str(int(x)))
    row = preds[preds['Customer ID'] == customer].iloc[0]
    prob = row['Churn_Probability'] * 100

    left, right = st.columns([1, 1])
    with left:
        gauge = go.Figure(go.Indicator(
            mode="gauge+number", value=prob, number={'suffix': '%'},
            title={'text': 'Churn risk'},
            gauge={'axis': {'range': [0, 100]},
                   'bar': {'color': '#1F2937'},
                   'steps': [{'range': [0, THRESHOLD * 100], 'color': '#D1FAE5'},
                             {'range': [THRESHOLD * 100, 70], 'color': '#FEF3C7'},
                             {'range': [70, 100], 'color': '#FEE2E2'}]}))
        gauge.update_layout(height=280, margin=dict(l=40, r=40, t=50, b=10))
        st.plotly_chart(gauge, use_container_width=True)
    with right:
        st.metric("Group", row['ClusterName'])
        st.metric("Days since last order", f"{int(row['Recency'])}")
        st.metric("Orders / Total spend", f"{int(row['Frequency'])} / £{row['Monetary']:,.0f}")

    if row['Risk'] == 'High':
        st.error("High risk: contact this customer soon with a personal offer.")
    elif row['Risk'] == 'Medium':
        st.warning("Medium risk: send a reminder or a small offer to bring them back.")
    else:
        st.success("Low risk: this customer is likely to buy again.")
st.caption("The 0.45 cut-off was chosen to catch more churners, so some customers flagged here "
           "may still buy again. Use the risk % to decide who to contact first.")