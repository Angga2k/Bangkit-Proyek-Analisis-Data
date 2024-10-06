import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Functions for analysis
def sales_by_review_score(df):
    sales_by_review_score = df.groupby('review_score')['order_id'].count().reset_index(name='sales_count')
    return sales_by_review_score

def order_payments(df):
    order_payments = df.groupby('payment_type')['order_id'].count().reset_index(name='payment_count').sort_values(by='payment_count', ascending=False)
    return order_payments

def order_payments_value(df):
    payment_value_analysis = df.groupby('payment_type')['payment_value'].mean().reset_index(name='average_payment_value')
    payment_value_analysis.drop(payment_value_analysis[payment_value_analysis['payment_type'] == 'not_defined'].index, inplace=True)
    return payment_value_analysis

def rfm_analysis(df):
    rfm_df = df.groupby(by="customer_id", as_index=False).agg({
        'order_purchase_timestamp': 'max',
        'order_id': 'nunique',
        'price': 'sum'
    })

    rfm_df.columns = ["customer_id", "max_order_timestamp", "frequency", "monetary"]
    rfm_df["max_order_timestamp"] = rfm_df["max_order_timestamp"].dt.date
    recent_date = df["order_purchase_timestamp"].dt.date.max()
    rfm_df["recency"] = rfm_df["max_order_timestamp"].apply(lambda x: (recent_date - x).days)
    rfm_df.drop("max_order_timestamp", axis=1, inplace=True)
    return rfm_df

# Load the data directly from a CSV file
main_df = pd.read_csv("dashboard/main_data.csv", parse_dates=['order_purchase_timestamp', 'order_approved_at', 'order_delivered_carrier_date', 'order_delivered_customer_date', 'order_estimated_delivery_date'])
review_by_review_score_df = pd.read_csv("data/order_items_and_reviews.csv")
order_payments_df = pd.read_csv("data/order_payments_and_orders.csv", parse_dates=['order_purchase_timestamp', 'order_approved_at', 'order_delivered_carrier_date', 'order_delivered_customer_date', 'order_estimated_delivery_date'])

# Streamlit app setup
st.title("😁 E Commerce Public Dataset Dashboard")
st.write("This dashboard presents the Recency, Frequency, and Monetary value of customers, and explores the impact of review scores on sales.")

# Sidebar with date filters
min_date = main_df['order_purchase_timestamp'].min().date()
max_date = main_df['order_purchase_timestamp'].max().date()

with st.sidebar:
    st.image("https://raw.githubusercontent.com/angga2k/logo/refs/heads/main/logo.png")
    start_date, end_date = st.date_input(
        label='Rentang Waktu Untuk RFM', 
        value=[min_date, max_date]
    )

# Filter the main DataFrame based on the selected date range
filtered_main_df = main_df[
    (main_df['order_purchase_timestamp'].dt.date >= start_date) &
    (main_df['order_purchase_timestamp'].dt.date <= end_date)
]

# Analysis after filtering
rfm_df = rfm_analysis(filtered_main_df)
sales_review_df = sales_by_review_score(review_by_review_score_df)
payment_method_frequency_df = order_payments(order_payments_df)
order_payments_value_df = order_payments_value(order_payments_df)

# Scatter plot for Sales by Review Score
st.subheader("Sales by Review Score")
st.metric(f"Total Review: ", value=sales_review_df['sales_count'].sum())
sns.set_style("whitegrid")
plt.figure(figsize=(10, 6))

# Color palette and scatter plot with varying marker sizes
palette = sns.color_palette("viridis", as_cmap=False)
ax = sns.scatterplot(
    data=sales_review_df, 
    x='review_score', 
    y='sales_count', 
    size='sales_count',  
    sizes=(50, 500),     
    hue='sales_count',   
    palette=palette, 
    alpha=0.7            
)

# Add regression line to show the trend
sns.regplot(
    data=sales_review_df, 
    x='review_score', 
    y='sales_count', 
    scatter=False, 
    color='red', 
    line_kws={'label': 'Linear Trend'}
)

# Customize title and labels
plt.title('Impact of Review Scores on Sales', fontsize=16, fontweight='bold')
plt.xlabel('Review Score', fontsize=12)
plt.ylabel('Sales Count', fontsize=12)

# Show legend
plt.legend()

# Display the scatter plot in Streamlit
st.pyplot(plt)
plt.clf()  # Clear plot to avoid overlap

palette="Blues"
# Payment Method Frequency Barplot
st.subheader("Payment Method Frequency")
sns.set_style("whitegrid")
plt.figure(figsize=(10, 6))

# Plot frequency of payment methods with annotations
ax = sns.barplot(data=payment_method_frequency_df, x='payment_type', y='payment_count', palette=palette)
plt.title('Frekuensi Penggunaan Metode Pembayaran', fontsize=16, fontweight='bold')
plt.xlabel('Metode Pembayaran', fontsize=12)
plt.ylabel('Jumlah Penggunaan', fontsize=12)

# Add annotations on the bars
for p in ax.patches:
    ax.annotate(format(p.get_height(), '.0f'), 
                (p.get_x() + p.get_width() / 2., p.get_height()), 
                ha='center', va='center', xytext=(0, 10), 
                textcoords='offset points', fontsize=10, color='black', fontweight='bold')

# Show the plot in Streamlit
st.pyplot(plt)
plt.clf()  # Clear plot to avoid overlap

# Average Payment Value Barplot
st.subheader("Average Order Value by Payment Method")
plt.figure(figsize=(10, 6))
ax2 = sns.barplot(data=order_payments_value_df, x='payment_type', y='average_payment_value', palette=palette)
plt.title('Rata-rata Nilai Pesanan per Metode Pembayaran', fontsize=16, fontweight='bold')
plt.xlabel('Metode Pembayaran', fontsize=12)
plt.ylabel('Rata-rata Nilai Pesanan', fontsize=12)

# Add annotations on the bars
for p in ax2.patches:
    ax2.annotate(format(p.get_height(), '.2f'), 
                (p.get_x() + p.get_width() / 2., p.get_height()), 
                ha='center', va='center', xytext=(0, 10), 
                textcoords='offset points', fontsize=10, color='black', fontweight='bold')

# Show the plot in Streamlit
st.pyplot(plt)
plt.clf()  # Clear plot to avoid overlap

# RFM Analysis: Top Customers by RFM Parameters
st.subheader("Top Customers by RFM Parameters")
rfm_df['short_customer_id'] = rfm_df['customer_id'].apply(lambda x: x[:8])  # Display first 8 characters

# Set up the plot layout with Streamlit
fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(30, 6))

# Use different color palette for RFM bars
colors = ["#A66E38", "#A66E38", "#A66E38", "#A66E38", "#A66E38"]

sns.barplot(y="recency", x="short_customer_id", data=rfm_df.sort_values(by="recency", ascending=True).head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].set_title("By Recency (days)", loc="center", fontsize=18)
ax[0].tick_params(axis='x', labelsize=15)

sns.barplot(y="frequency", x="short_customer_id", data=rfm_df.sort_values(by="frequency", ascending=False).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].set_title("By Frequency", loc="center", fontsize=18)
ax[1].tick_params(axis='x', labelsize=15)

sns.barplot(y="monetary", x="short_customer_id", data=rfm_df.sort_values(by="monetary", ascending=False).head(5), palette=colors, ax=ax[2])
ax[2].set_ylabel(None)
ax[2].set_xlabel(None)
ax[2].set_title("By Monetary", loc="center", fontsize=18)
ax[2].tick_params(axis='x', labelsize=15)

for axis in ax:
    axis.tick_params(axis='x', rotation=45)

# Display the RFM analysis plot in Streamlit
st.pyplot(fig)

st.caption('Copyright Angga Dwi Kurniawan 2024')
