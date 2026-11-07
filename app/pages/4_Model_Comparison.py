"""
Page 4: Model Comparison
Shows how all my models performed (Phases 4 to 6) and why I chose the final model.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from utils import load_results, load_importance, apply_style

st.set_page_config(page_title="Model Comparison", page_icon="🏆", layout="wide")
apply_style()

st.title("🏆 Model Comparison")
st.caption("All models were tested on the same 1,052 customers that were never used for training.")

# Results from Phase 5, plus the tuned XGBoost from Phase 6 (numbers from my Phase 6 notebook)
results = load_results()
tuned = pd.DataFrame([{
    'Model': 'XGBoost (tuned)', 'Accuracy': 0.740, 'Precision': 0.749, 'Recall': 0.810,
    'F1': 0.778, 'ROC_AUC': 0.797, 'Train_ROC_AUC': 0.866, 'CV_ROC_AUC': 0.809,
}])
results = pd.concat([results, tuned], ignore_index=True).sort_values('ROC_AUC', ascending=False)
for col in ['Accuracy', 'Precision', 'Recall', 'F1', 'ROC_AUC', 'Train_ROC_AUC', 'CV_ROC_AUC']:
    results[col] = results[col].astype(float)
# ---------- KPI cards: the final model ----------
k1, k2, k3, k4 = st.columns(4)
k1.metric("Final model (tuned)", "XGBoost")
k2.metric("Test ROC-AUC", "0.797")
k3.metric("Recall (cut-off 0.45)", "0.870")
k4.metric("Churners missed", "77", delta="45 fewer than baseline", delta_color="normal")

chart_layout = dict(plot_bgcolor="white", paper_bgcolor="white",
                    margin=dict(l=10, r=10, t=10, b=10), height=350)

# ---------- Results table ----------
with st.container(border=True):
    st.subheader("All models on all metrics")
    st.caption("Green = best value in each column. Scores use the default cut-off of 0.5. "
               "The decision tree was not cross-validated, so it has no CV score.")
    metric_cols = ['Accuracy', 'Precision', 'Recall', 'F1', 'ROC_AUC', 'CV_ROC_AUC']
    score_cols = metric_cols + ['Train_ROC_AUC']

    # Numbers shown as text, with a dash for missing values
    display = results.copy()
    for c in score_cols:
        display[c] = results[c].map(lambda v: '-' if pd.isna(v) else f'{v:.3f}')

    # Find the best value in each column (using the real numbers)
    best = results[metric_cols].eq(results[metric_cols].max())

    def color_best(_):
        css = pd.DataFrame('', index=display.index, columns=display.columns)
        css[metric_cols] = best.replace({True: 'background-color: #D1FAE5', False: ''})
        return css

    st.dataframe(display.style.apply(color_best, axis=None),
                 hide_index=True, use_container_width=True)

# ---------- Row 1: ROC-AUC and overfitting ----------
col1, col2 = st.columns(2)

with col1:
    with st.container(border=True):
        st.subheader("Test vs cross-validation ROC-AUC")
        auc = results.melt(id_vars='Model', value_vars=['ROC_AUC', 'CV_ROC_AUC'],
                           var_name='Score', value_name='Value').dropna()
        auc['Score'] = auc['Score'].map({'ROC_AUC': 'Test', 'CV_ROC_AUC': 'Cross-validation'})
        fig = px.bar(auc, x='Value', y='Model', color='Score', barmode='group', orientation='h',
                     color_discrete_sequence=['#4F46E5', '#A5B4FC'])
        fig.update_layout(**chart_layout, xaxis_range=[0.7, 0.83], yaxis_title='',
                          xaxis_title='ROC-AUC', legend_title_text='')
        st.plotly_chart(fig, use_container_width=True)

with col2:
    with st.container(border=True):
        st.subheader("Overfitting check: train vs test")
        gap = results.melt(id_vars='Model', value_vars=['Train_ROC_AUC', 'ROC_AUC'],
                           var_name='Data', value_name='Value')
        gap['Data'] = gap['Data'].map({'Train_ROC_AUC': 'Train', 'ROC_AUC': 'Test'})
        fig = px.bar(gap, x='Value', y='Model', color='Data', barmode='group', orientation='h',
                     color_discrete_sequence=['#F59E0B', '#4F46E5'])
        fig.update_layout(**chart_layout, xaxis_range=[0.7, 1.0], yaxis_title='',
                          xaxis_title='ROC-AUC', legend_title_text='')
        st.plotly_chart(fig, use_container_width=True)
        st.caption("A big gap between train and test means the model memorised the training data.")

# ---------- Row 2: cut-off and feature importance ----------
col3, col4 = st.columns(2)

with col3:
    with st.container(border=True):
        st.subheader("Effect of the cut-off (test set)")
        cutoff = pd.DataFrame({
            'Cut-off': ['0.50 (default)', '0.45 (chosen)'],
            'Recall': [0.810, 0.870], 'Precision': [0.749, 0.719],
        }).melt(id_vars='Cut-off', var_name='Metric', value_name='Value')
        fig = px.bar(cutoff, x='Cut-off', y='Value', color='Metric', barmode='group',
                     text=cutoff['Value'].map('{:.3f}'.format),
                     color_discrete_sequence=['#10B981', '#0EA5E9'])
        fig.update_layout(**chart_layout, yaxis_range=[0, 1], xaxis_title='',
                          yaxis_title='Score', legend_title_text='')
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Missed churners went down from 113 to 77, for a small drop in precision.")

with col4:
    with st.container(border=True):
        st.subheader("Most important features")
        imp = load_importance().sort_values('Importance')
        fig = px.bar(imp, x='Importance', y='Feature', orientation='h',
                     color_discrete_sequence=['#4F46E5'])
        fig.update_layout(**chart_layout, yaxis_title='',
                          xaxis_title='Drop in ROC-AUC')
        st.plotly_chart(fig, use_container_width=True)

# ---------- Why this model ----------
with st.container(border=True):
    st.subheader("Why I chose the tuned XGBoost")
    st.markdown("""
- **Best ranking of churners:** highest cross-validation ROC-AUC (0.809) and joint-highest test ROC-AUC (0.797).
- **Catches the most churners:** highest recall of all models, and with the 0.45 cut-off it catches 87% of churners.
- **Less overfitting:** smaller gap between train and test than Random Forest and Stacking.
- **Simpler than Stacking:** Stacking with the tuned XGBoost had the same ROC-AUC but lower recall, and it uses 4 models instead of 1.
- **Easy to explain:** with SHAP I could show that Recency is the strongest sign of churn.
""")