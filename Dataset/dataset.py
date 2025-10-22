import pandas as pd
import numpy as np
from faker import Faker
from datetime import datetime, timedelta
import random

# -----------------------------
# CONFIGURATION
# -----------------------------
NUM_ROWS = 5000
fake = Faker('en_US')
FILE_NAME = 'Business_Performance_Data_Enhanced.csv'

# Generate data for the past 18 months
CURRENT_TIME = datetime.now()
START_DATE = CURRENT_TIME - timedelta(days=540)

REGIONS = ['North', 'South', 'East', 'West']
PRODUCT_CATEGORIES = ['Electronics', 'Services', 'Software', 'Apparel']
PRODUCT_NAMES = {
    'Electronics': ['Deluxe Widget', 'Smart Monitor', 'E-Reader', 'Wireless Headphones'],
    'Services': ['Consulting Hour', 'Maintenance Contract', 'Premium Support', 'Installation Service'],
    'Software': ['Cloud Subscription', 'Data Analytics Tool', 'ERP Module', 'CRM Suite'],
    'Apparel': ['T-Shirt', 'Polo Shirt', 'Jacket', 'Hoodie']
}
CUSTOMER_SEGMENTS = ['Retail', 'Wholesale', 'Online']
CAMPAIGN_NAMES = ['Spring Promo', 'Summer Sale', 'Holiday Sale', 'Back-to-School', 'Q1 Launch']

# -----------------------------
# DATA GENERATION FUNCTION
# -----------------------------
def generate_business_data(num_records):
    records = []
    
    for _ in range(num_records):
        # --- General Business Attributes ---
        # Random date within the last 18 months
        transaction_date = START_DATE + timedelta(days=random.randint(0, 540))
        region = np.random.choice(REGIONS, p=[0.25, 0.25, 0.25, 0.25])
        category = np.random.choice(PRODUCT_CATEGORIES, p=[0.3, 0.2, 0.3, 0.2])
        product_name = np.random.choice(PRODUCT_NAMES[category])
        
        # --- Sales and Operations Metrics ---
        customer_segment = np.random.choice(CUSTOMER_SEGMENTS, p=[0.4, 0.1, 0.5])
        campaign_name = np.random.choice(CAMPAIGN_NAMES)
        units_sold = np.random.randint(10, 300)
        
        # --- Base price logic by category ---
        if category == 'Electronics':
            base_price = np.random.uniform(150, 800)
        elif category == 'Software':
            base_price = np.random.uniform(500, 2500)
        elif category == 'Services':
            base_price = np.random.uniform(100, 600)
        else: # Apparel
            base_price = np.random.uniform(20, 150)
            
        # --- Revenue influenced by region and campaign (Simulated Bias/Performance) ---
        revenue = units_sold * base_price
        
        # North region bias for Electronics
        if region == 'North' and category == 'Electronics':
            revenue *= 1.15
        
        # South region bias for Apparel
        if region == 'South' and category == 'Apparel':
            revenue *= 1.2
            
        # Campaign performance bias
        if 'Holiday' in campaign_name:
            revenue *= 1.25
        if 'Summer' in campaign_name:
            revenue *= 1.1
            
        # --- Cost and profit logic ---
        cost = revenue * np.random.uniform(0.5, 0.75)
        profit = revenue - cost
        profit_margin = round((profit / revenue) * 100, 2)
        
        # --- Inventory and returns (Physical Goods only) ---
        if category in ['Electronics', 'Apparel']:
            inventory_level = np.random.randint(100, 5000)
            return_rate = np.random.uniform(0.01, 0.1)
        else:
            inventory_level = np.nan # Use NaN for non-physical goods
            return_rate = 0.0
            
        # --- Customer and satisfaction ---
        order_id = f"ORD-{random.randint(100000,999999)}"
        customer_id = f"CUST-{np.random.randint(10000, 99999)}"
        conversion_rate = np.random.uniform(0.02, 0.15)
        satisfaction_score = np.random.choice([1, 2, 3, 4, 5], p=[0.05, 0.1, 0.2, 0.4, 0.25])
        
        # --- Time attributes (Derived) ---
        month = transaction_date.strftime('%Y-%m')
        quarter = f"{transaction_date.year}-Q{(transaction_date.month - 1)//3 + 1}"
        year = transaction_date.year
        week_number = transaction_date.isocalendar()[1]
        
        # --- Derived metrics ---
        avg_order_value = revenue / units_sold

        # Build the record list
        record = [
            transaction_date.strftime('%Y-%m-%d'), 
            region, 
            product_name, 
            category, 
            round(revenue, 2), 
            round(cost, 2), 
            round(profit, 2), 
            profit_margin, 
            units_sold, 
            inventory_level, 
            round(return_rate, 3), 
            order_id,
            customer_id, 
            customer_segment, 
            campaign_name, 
            round(conversion_rate, 3), 
            satisfaction_score, 
            round(avg_order_value, 2), 
            month, 
            quarter, 
            year, 
            week_number
        ]
        records.append(record)
        
    return records

# -----------------------------
# GENERATE AND SAVE DATA
# -----------------------------
print(f"Generating {NUM_ROWS} rows of enhanced business performance data...")
data = generate_business_data(NUM_ROWS)

columns = [
    'Date', 'Region', 'Product_Service_Name', 'Category_Department', 
    'Revenue', 'Cost', 'Profit', 'Profit_Margin_pct', 
    'Units_Sold', 'Inventory_Level', 'Return_Rate_pct', 'Order_ID', 
    'Customer_ID', 'Customer_Segment', 'Campaign_Name', 'Conversion_Rate_pct', 
    'Customer_Satisfaction_Score', 
    'Average_Order_Value', 
    'Month', 'Quarter', 'Year', 'Week_Number'
]

df = pd.DataFrame(data, columns=columns)

# Clean data types (important for analysis/chatbots)
df['Inventory_Level'] = pd.to_numeric(df['Inventory_Level'], errors='coerce')
df['Customer_Satisfaction_Score'] = pd.to_numeric(df['Customer_Satisfaction_Score'], errors='coerce')

# Save to CSV
df.to_csv(FILE_NAME, index=False)

print(f"\n✅ Data generation complete.")
print(f"File saved as: {FILE_NAME}")
print(f"First transaction date: {df['Date'].min()}")
print(f"Last transaction date: {df['Date'].max()}")
print(f"Total records: {len(df)}")