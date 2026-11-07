# Online Retail: Customer Analytics and Churn Prediction

In this project I used sales data from a UK online gift shop to understand its customers and predict which customers might stop buying (churn).

I started with a data analysis project and extended it into a full machine learning project with EDA, unsupervised learning, supervised learning, ensemble learning, model tuning and a Streamlit app.

## Dataset

- **Online Retail II** dataset (UCI Machine Learning Repository)
- A UK online shop that sells gifts, many of its customers are wholesalers
- Data from December 2009 to December 2011
- After cleaning: 776,594 rows, 5,852 customers, 36,592 orders and £16.8 million in revenue

## What I did

### Phase 1: Cleaning, EDA and RFM segments
- I removed duplicates, cancelled orders, missing customer IDs and non-product rows like postage.
- I looked at sales by month, country, product and time of day. Sales are highest in November because of Christmas.
- I grouped customers with RFM (Recency, Frequency, Monetary) using rules, for example Champions, Loyal, At Risk and Lost.

### Phase 2: Feature engineering
- To predict churn fairly, I picked a cutoff date (11 September 2011). I built the features using only data before it, and checked who bought again in the next 90 days. This avoids data leakage.
- Churn = 1 means the customer did not buy in the 90 days after the cutoff.
- I made 12 features for each customer, like Recency, Frequency, Monetary, Tenure, average days between orders and orders in the last 90 days.
- 56.5% of customers churned, so the classes are fairly balanced.

### Phase 3: Customer clustering (unsupervised learning)
- I used K-Means on Recency, Frequency and Monetary. I used log and scaling first because the data was very skewed.
- I chose k = 4 using the elbow method and silhouette score.
- I compared the clusters with my RFM segments from Phase 1.

| Cluster | Customers | Revenue share |
|---|---|---|
| Champions | 1,183 | 73.5% |
| At Risk | 1,453 | 16.6% |
| New Customers | 1,246 | 6.2% |
| Lost Customers | 1,970 | 3.7% |

Champions are only 20% of customers but bring 73.5% of the revenue.

### Phase 4: Baseline models (supervised learning)
- I started with a dummy model that always predicts churn. It got 56.5% accuracy but ROC-AUC 0.5, so I used **ROC-AUC** as my main score.
- Logistic Regression was the best baseline (ROC-AUC 0.789).
- A decision tree with no limit overfitted badly (train 1.0, test 0.641), so I limited its depth.

### Phase 5: Ensemble learning
- I tried Random Forest (bagging), XGBoost (boosting) and Stacking.
- All models were close, but Stacking and XGBoost were a little better than Logistic Regression.

### Phase 6: Model tuning and explanation
- I tuned XGBoost with RandomizedSearchCV. It became my final model.
- I changed the cut-off from 0.5 to 0.45 to catch more churners.
- I used permutation importance and SHAP to see which features drive churn.

### Phase 7: Streamlit app
I built an app with 4 pages:
- **Sales Dashboard:** sales KPIs and charts with date and country filters
- **Customer Segments:** the 4 clusters, their profiles and a customer lookup
- **Churn Predictor:** churn risk for every customer, a list of customers to contact (can be downloaded) and a check for one customer
- **Model Comparison:** all models compared and why I chose the final model

## Results

| Model | Accuracy | Recall | F1 | Test ROC-AUC | CV ROC-AUC |
|---|---|---|---|---|---|
| Dummy | 0.565 | 1.000 | 0.722 | 0.500 | - |
| Decision Tree (depth 5) | 0.718 | 0.781 | 0.758 | 0.769 | - |
| Logistic Regression | 0.735 | 0.795 | 0.772 | 0.789 | 0.801 |
| Random Forest | 0.736 | 0.778 | 0.769 | 0.788 | 0.803 |
| XGBoost | 0.722 | 0.785 | 0.761 | 0.792 | 0.805 |
| Stacking | 0.736 | 0.786 | 0.771 | 0.796 | 0.808 |
| **XGBoost (tuned)** | **0.740** | **0.810** | **0.778** | **0.797** | **0.809** |

(These scores use the default cut-off of 0.5.)

**Final model: tuned XGBoost with a cut-off of 0.45**
- Recall 0.870, so it catches 87% of the customers who churn
- Precision 0.719
- It misses only 77 churners, compared with 122 for Logistic Regression

**Why I chose it:** it has the best ROC-AUC on cross-validation, the highest recall, less overfitting than Random Forest and Stacking, and it is simpler than Stacking.

## Key findings

- **Recency is the strongest sign of churn.** Customers who have not bought for a long time are the most likely to leave.
- Customers who spend more, buy many different products and order often are more likely to stay.
- Customers who usually buy in October to December are more likely to come back for Christmas.
- Country (UK or not) has almost no effect on churn.

## What the business can do

- Contact customers early when the time since their last order starts growing.
- Send reminders or small offers to customers who take a long time between orders.
- Show more products to customers who only buy a few, because customers who buy many products stay longer.
- Try to win customers back before the October to December season.

## Project structure

```
data/
├── data/
│   ├── raw/              # original Excel file
│   └── processed/        # cleaned data and feature tables
├── models/               # saved models and results
├── Notebooks/
│   ├── 01_cleaning_eda_rfm.ipynb
│   ├── 02_feature_engineering.ipynb
│   ├── 03_clustering.ipynb
│   ├── 04_churn_baseline.ipynb
│   ├── 05_ensembles.ipynb
│   └── 06_tuning_explain.ipynb
├── app/
│   ├── Home.py
│   ├── utils.py
│   └── pages/
│       ├── 1_Sales_Dashboard.py
│       ├── 2_Customer_Segments.py
│       ├── 3_Churn_Predictor.py
│       └── 4_Model_Comparison.py
├── .streamlit/config.toml   # app colour theme
└── requirements.txt
```

## How to run

1. Install the packages:
   ```
   pip install -r requirements.txt
   ```
2. Run the notebooks in order (01 to 06). They create the data files and models the app needs.
3. Start the app from the project folder:
   ```
   python -m streamlit run app/Home.py
   ```

I built this project with Python 3.14.

## App screenshots

(Add screenshots of the app here.)

## What I learned

- How to avoid data leakage by using a cutoff date for the churn label.
- Accuracy alone can be misleading, so I compared models with several metrics and used ROC-AUC as my main score.
- A more complex model is not always much better. The ensembles only improved a little over Logistic Regression.
- Choosing the cut-off is a business decision, not only a technical one.
- How to turn my analysis into an interactive app with Streamlit.