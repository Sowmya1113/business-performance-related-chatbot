import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import re

st.set_page_config(
    page_title="Data Analyst Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        border-left: 4px solid #667eea;
    }
    
    .user-message {
        background-color: #f0f2f6;
        border-left-color: #667eea;
    }
    
    .bot-message {
        background-color: #e8f4fd;
        border-left-color: #1f77b4;
    }
    
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
    
    .insight-box {
        background: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'data' not in st.session_state:
    st.session_state.data = None

st.markdown("""
<div class="main-header">
    <h1>🤖 Data Analyst Chatbot</h1>
    <p>Upload your CSV and ask me anything about your business performance data!</p>
</div>
""", unsafe_allow_html=True)

@st.cache_data
def analyze_question(question, df):
    question_lower = question.lower()
    
    if any(word in question_lower for word in ['region', 'regional', 'geography', 'location']):
        return analyze_regional_performance(df)
    
    elif any(word in question_lower for word in ['monthly', 'trend', 'time', 'month', 'over time']):
        return analyze_monthly_trends(df)
    
    elif any(word in question_lower for word in ['profit', 'margin', 'profitability', 'cost']):
        return analyze_profit_margins(df)
    
    elif any(word in question_lower for word in ['campaign', 'marketing', 'promotion', 'channel']):
        return analyze_campaign_performance(df)
    
    elif any(word in question_lower for word in ['satisfaction', 'customer', 'rating', 'score']):
        return analyze_customer_satisfaction(df)
    
    elif any(word in question_lower for word in ['inventory', 'stock', 'warehouse', 'levels']):
        return analyze_inventory(df)
    
    elif any(word in question_lower for word in ['category', 'product', 'department', 'service']):
        return analyze_category_performance(df)
    
    elif any(word in question_lower for word in ['summary', 'overview', 'general', 'what is the data showing']):
        return generate_summary(df)
    
    else:
        return {"text": "I can help you analyze various aspects of your business data. Try asking about **regional performance**, **monthly trends**, **profit margins**, **campaign effectiveness**, **customer satisfaction**, or **inventory levels**."}

@st.cache_data
def analyze_regional_performance(df):
    if 'Region' not in df.columns or 'Revenue' not in df.columns:
        return {"text": "Regional analysis requires 'Region' and 'Revenue' columns in your data."}
    
    regional_data = df.groupby('Region').agg({
        'Revenue': 'sum',
        'Profit': 'sum',
        'Units_Sold': 'sum'
    }).round(2)
    
    regional_data['Profit_Margin'] = (regional_data['Profit'] / regional_data['Revenue'] * 100).round(2).fillna(0)
    regional_data = regional_data.sort_values('Revenue', ascending=False)
    
    fig = px.bar(
        regional_data.reset_index(),
        x='Region',
        y='Revenue',
        title="Revenue by Region",
        labels={'x': 'Region', 'y': 'Revenue ($)'},
        color='Revenue',
        color_continuous_scale='Blues',
        hover_data=['Profit', 'Profit_Margin']
    )
    fig.update_layout(showlegend=False)
    
    top_region = regional_data.index[0]
    top_revenue = regional_data.loc[top_region, 'Revenue']
    total_revenue = regional_data['Revenue'].sum()
    top_percentage = (top_revenue / total_revenue * 100).round(1)
    
    text = f"""
    ## 📍 Regional Performance Analysis
    
    **Key Insights:**
    - **Top Performing Region:** **{top_region}** (${top_revenue:,.0f} - {top_percentage}% of total revenue)
    - **Total Revenue Across All Regions:** ${total_revenue:,.0f}
    
    **Detailed Breakdown:**
    """
    
    for region in regional_data.index:
        revenue = regional_data.loc[region, 'Revenue']
        margin = regional_data.loc[region, 'Profit_Margin']
        text += f"\n- **{region}:** ${revenue:,.0f} revenue, {margin}% profit margin"
    
    return {
        "text": text,
        "chart": fig,
        "dataframe": regional_data
    }

@st.cache_data
def analyze_monthly_trends(df):
    if 'Date' not in df.columns or 'Revenue' not in df.columns:
        return {"text": "Monthly trend analysis requires 'Date' (datetime format) and 'Revenue' columns in your data."}
    
    df_temp = df.copy()
    df_temp['Month'] = df_temp['Date'].dt.to_period('M')
    
    monthly_data = df_temp.groupby('Month').agg({
        'Revenue': 'sum',
        'Units_Sold': 'sum',
        'Profit': 'sum'
    }).round(2)
    
    monthly_data.index = monthly_data.index.astype(str)
    
    monthly_data['Revenue_Growth'] = monthly_data['Revenue'].pct_change() * 100
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=monthly_data.index,
        y=monthly_data['Revenue'],
        mode='lines+markers',
        name='Revenue',
        line=dict(color='#1f77b4', width=3)
    ))
    
    fig.update_layout(
        title="Monthly Revenue Trends",
        xaxis_title="Month",
        yaxis_title="Revenue ($)",
        hovermode='x unified'
    )
    
    latest_month = monthly_data.index[-1]
    latest_revenue = monthly_data.loc[latest_month, 'Revenue']
    latest_growth = monthly_data.loc[latest_month, 'Revenue_Growth']
    
    best_month = monthly_data['Revenue'].idxmax()
    best_revenue = monthly_data.loc[best_month, 'Revenue']
    
    text = f"""
    ## 📈 Monthly Revenue Trends Analysis
    
    **Key Insights:**
    - **Latest Month ({latest_month}):** **${latest_revenue:,.0f}**
    - **Month-over-Month Growth:** {latest_growth:.1f}%
    - **Best Performing Month:** {best_month} (${best_revenue:,.0f})
    - **Average Monthly Revenue:** ${monthly_data['Revenue'].mean():,.0f}
    
    **Trend Analysis:**
    The chart shows your revenue progression over time. Look for **seasonal patterns** and **growth opportunities**.
    """
    
    return {
        "text": text,
        "chart": fig,
        "dataframe": monthly_data
    }

@st.cache_data
def analyze_profit_margins(df):
    if 'Profit' not in df.columns or 'Revenue' not in df.columns:
        return {"text": "Profit analysis requires 'Profit' and 'Revenue' columns in your data."}
    
    group_col = 'Product_Service_Name' if 'Product_Service_Name' in df.columns else 'Category_Department'
    
    if group_col not in df.columns:
        return {"text": "Profit analysis requires a 'Product_Service_Name' or 'Category_Department' column in your data."}
    
    profit_data = df.groupby(group_col).agg({
        'Revenue': 'sum',
        'Profit': 'sum',
        'Units_Sold': 'sum'
    }).round(2)
    
    profit_data['Profit_Margin'] = (profit_data['Profit'] / profit_data['Revenue'] * 100).round(2).fillna(0)
    profit_data = profit_data.sort_values('Profit_Margin', ascending=False)
    
    df_chart = profit_data.head(10).reset_index()
    fig = px.bar(
        df_chart,
        x='Profit_Margin',
        y=group_col,
        orientation='h',
        title=f"Top 10 {group_col.replace('_', ' ')} by Profit Margin",
        labels={'x': 'Profit Margin (%)', 'y': group_col.replace('_', ' ')},
        color='Profit_Margin',
        color_continuous_scale='Greens'
    )
    
    top_item = profit_data.index[0]
    top_margin = profit_data.loc[top_item, 'Profit_Margin']
    avg_margin = profit_data['Profit_Margin'].mean()
    
    text = f"""
    ## 💰 Profit Margin Analysis
    
    **Key Insights:**
    - **Highest Margin:** **{top_item}** ({top_margin}%)
    - **Average Margin:** {avg_margin:.1f}%
    - **Focus:** Analyze high-margin products to understand cost structures and pricing strategies.
    
    **Top 5 Performers:**
    """
    
    for i, item in enumerate(profit_data.index[:5]):
        margin = profit_data.loc[item, 'Profit_Margin']
        revenue = profit_data.loc[item, 'Revenue']
        text += f"\n{i+1}. **{item}:** {margin}% margin (${revenue:,.0f} revenue)"
    
    return {
        "text": text,
        "chart": fig,
        "dataframe": profit_data.head(10)
    }

@st.cache_data
def analyze_campaign_performance(df):
    if 'Campaign_Name' not in df.columns or 'Revenue' not in df.columns:
        return {"text": "Campaign analysis requires 'Campaign_Name' and 'Revenue' columns in your data."}
    
    campaign_data = df.groupby('Campaign_Name').agg({
        'Revenue': 'sum',
        'Units_Sold': 'sum',
        'Profit': 'sum'
    }).round(2)
    
    campaign_data['Avg_Order_Value'] = (campaign_data['Revenue'] / df.groupby('Campaign_Name').size()).round(2).fillna(0)
    campaign_data = campaign_data.sort_values('Revenue', ascending=False)
    
    fig = px.pie(
        campaign_data.reset_index(),
        values='Revenue',
        names='Campaign_Name',
        title="Revenue Distribution by Campaign"
    )
    
    best_campaign = campaign_data.index[0]
    best_revenue = campaign_data.loc[best_campaign, 'Revenue']
    total_revenue = campaign_data['Revenue'].sum()
    best_percentage = (best_revenue / total_revenue * 100).round(1)
    
    text = f"""
    ## 🎯 Campaign Performance Analysis
    
    **Key Insights:**
    - **Top Campaign:** **{best_campaign}** (${best_revenue:,.0f} - {best_percentage}% of total revenue)
    - **Total Campaigns:** {len(campaign_data)}
    - **Total Campaign Revenue:** ${total_revenue:,.0f}
    
    **Campaign Breakdown:**
    """
    
    for campaign in campaign_data.index:
        revenue = campaign_data.loc[campaign, 'Revenue']
        aov = campaign_data.loc[campaign, 'Avg_Order_Value']
        text += f"\n- **{campaign}:** ${revenue:,.0f} revenue, **${aov:.0f}** avg order value"
    
    return {
        "text": text,
        "chart": fig,
        "dataframe": campaign_data
    }

@st.cache_data
def analyze_customer_satisfaction(df):
    if 'Customer_Satisfaction_Score' not in df.columns:
        return {"text": "Customer satisfaction analysis requires a 'Customer_Satisfaction_Score' column (0-5 scale) in your data."}
    
    avg_satisfaction = df['Customer_Satisfaction_Score'].mean()
    satisfaction_counts = df['Customer_Satisfaction_Score'].value_counts().sort_index()
    
    if 'Region' in df.columns:
        region_satisfaction = df.groupby('Region')['Customer_Satisfaction_Score'].mean().round(2)
        region_satisfaction = region_satisfaction.sort_values(ascending=False)
        
        fig = px.bar(
            region_satisfaction.reset_index(),
            x='Region',
            y='Customer_Satisfaction_Score',
            title="Average Customer Satisfaction by Region",
            labels={'x': 'Region', 'y': 'Average Satisfaction Score'},
            color='Customer_Satisfaction_Score',
            color_continuous_scale='RdYlGn'
        )
        fig.update_layout(yaxis=dict(range=[0, 5]))
        
        text = f"""
        ## 😊 Customer Satisfaction Analysis
        
        **Overall Insights:**
        - **Average Satisfaction:** **{avg_satisfaction:.2f}/5.0**
        - **Total Responses:** {len(df):,}
        
        **By Region:**
        """
        
        for region in region_satisfaction.index:
            score = region_satisfaction[region]
            emoji = "🟢" if score >= 4 else "🟡" if score >= 3 else "🔴"
            text += f"\n{emoji} **{region}:** {score}/5.0"
        
        return {
            "text": text,
            "chart": fig,
            "dataframe": region_satisfaction.to_frame('Avg_Satisfaction')
        }
    
    else:
        df_chart = satisfaction_counts.reset_index()
        df_chart.columns = ['Score', 'Count']
        fig = px.bar(
            df_chart,
            x='Score',
            y='Count',
            title="Customer Satisfaction Score Distribution",
            labels={'Score': 'Satisfaction Score', 'Count': 'Number of Responses'},
            color='Score',
            color_continuous_scale='Viridis'
        )
        
        text = f"""
        ## 😊 Customer Satisfaction Analysis
        
        **Overall Insights:**
        - **Average Satisfaction:** **{avg_satisfaction:.2f}/5.0**
        - **Total Responses:** {len(df):,}
        
        **Score Distribution:**
        """
        
        for score in satisfaction_counts.index:
            count = satisfaction_counts[score]
            percentage = (count / len(df) * 100).round(1)
            text += f"\n- **{int(score)} stars:** {count:,} responses ({percentage}%)"
        
        return {
            "text": text,
            "chart": fig
        }

@st.cache_data
def analyze_inventory(df):
    if 'Inventory_Level' not in df.columns or 'Category_Department' not in df.columns:
        return {"text": "Inventory analysis requires 'Inventory_Level' and 'Category_Department' columns in your data."}
    
    inventory_df = df[df['Inventory_Level'].notna()].copy()
    
    if len(inventory_df) == 0:
        return {"text": "No inventory data available for analysis."}
    
    inventory_by_category = inventory_df.groupby('Category_Department').agg({
        'Inventory_Level': ['mean', 'sum', 'count']
    }).round(0)
    
    inventory_by_category.columns = ['Avg_Inventory', 'Total_Inventory', 'Product_Count']
    inventory_by_category = inventory_by_category.sort_values('Total_Inventory', ascending=False)
    
    fig = px.bar(
        inventory_by_category.reset_index(),
        x='Category_Department',
        y='Total_Inventory',
        title="Total Inventory by Category",
        labels={'Category_Department': 'Category', 'Total_Inventory': 'Total Inventory Units'},
        color='Total_Inventory',
        color_continuous_scale='Blues'
    )
    
    low_stock_threshold = inventory_df['Inventory_Level'].quantile(0.25)
    low_stock_items_count = len(inventory_df[inventory_df['Inventory_Level'] <= low_stock_threshold])
    
    text = f"""
    ## 📦 Inventory Analysis
    
    **Overall Insights:**
    - **Total Products with Inventory:** {len(inventory_df):,}
    - **Average Inventory Level:** **{inventory_df['Inventory_Level'].mean():,.0f}** units
    - **Low Stock Risk:** {low_stock_items_count:,} items are below the 25th percentile threshold of **{low_stock_threshold:.0f} units**.
    
    **By Category:**
    """
    
    for category in inventory_by_category.index:
        total = inventory_by_category.loc[category, 'Total_Inventory']
        avg = inventory_by_category.loc[category, 'Avg_Inventory']
        count = inventory_by_category.loc[category, 'Product_Count']
        text += f"\n- **{category}:** {total:,.0f} total units, {avg:,.0f} avg per product ({count} products)"
    
    return {
        "text": text,
        "chart": fig,
        "dataframe": inventory_by_category
    }

@st.cache_data
def analyze_category_performance(df):
    if 'Category_Department' not in df.columns or 'Revenue' not in df.columns or 'Profit' not in df.columns:
        return {"text": "Category analysis requires 'Category_Department', 'Revenue', and 'Profit' columns in your data."}
    
    category_data = df.groupby('Category_Department').agg({
        'Revenue': 'sum',
        'Profit': 'sum',
        'Units_Sold': 'sum'
    }).round(2)
    
    category_data['Profit_Margin'] = (category_data['Profit'] / category_data['Revenue'] * 100).round(2).fillna(0)
    category_data['Avg_Unit_Price'] = (category_data['Revenue'] / category_data['Units_Sold']).round(2).fillna(0)
    category_data = category_data.sort_values('Revenue', ascending=False)
    
    df_chart = category_data.reset_index()
    fig = px.scatter(
        df_chart,
        x='Revenue',
        y='Profit_Margin',
        size='Units_Sold',
        hover_name='Category_Department',
        title="Category Performance: Revenue vs Profit Margin (Bubble size = Units Sold)",
        labels={'Revenue': 'Revenue ($)', 'Profit_Margin': 'Profit Margin (%)'},
        size_max=60,
        color='Profit_Margin',
        color_continuous_scale=px.colors.sequential.Agsunset
    )
    
    top_revenue_category = category_data.index[0]
    top_margin_category = category_data['Profit_Margin'].idxmax()
    
    text = f"""
    ## 🏷️ Category Performance Analysis
    
    **Key Insights:**
    - **Highest Revenue:** **{top_revenue_category}** (${category_data.loc[top_revenue_category, 'Revenue']:,.0f})
    - **Highest Margin:** **{top_margin_category}** ({category_data.loc[top_margin_category, 'Profit_Margin']:.1f}%)
    - **Total Categories:** {len(category_data)}
    
    **Category Breakdown:**
    """
    
    for category in category_data.index:
        revenue = category_data.loc[category, 'Revenue']
        margin = category_data.loc[category, 'Profit_Margin']
        units = category_data.loc[category, 'Units_Sold']
        text += f"\n- **{category}:** ${revenue:,.0f} revenue, {margin:.1f}% margin, {units:,} units sold"
    
    return {
        "text": text,
        "chart": fig,
        "dataframe": category_data
    }

@st.cache_data
def generate_summary(df):
    total_revenue = df['Revenue'].sum() if 'Revenue' in df.columns else 0
    total_profit = df['Profit'].sum() if 'Profit' in df.columns else 0
    total_units = df['Units_Sold'].sum() if 'Units_Sold' in df.columns else 0
    
    overall_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0
    
    if 'Date' in df.columns and not df['Date'].empty:
        date_range = f"{df['Date'].min().strftime('%Y-%m-%d')} to {df['Date'].max().strftime('%Y-%m-%d')}"
    else:
        date_range = "Date information not available"
    
    top_region = df.groupby('Region')['Revenue'].sum().idxmax() if 'Region' in df.columns and 'Revenue' in df.columns else "N/A"
    top_category = df.groupby('Category_Department')['Revenue'].sum().idxmax() if 'Category_Department' in df.columns and 'Revenue' in df.columns else "N/A"
    
    text = f"""
    ## 📊 Business Performance Summary
    
    **Overall Performance:**
    - **Total Revenue:** **${total_revenue:,.0f}**
    - **Total Profit:** **${total_profit:,.0f}**
    - **Overall Profit Margin:** **{overall_margin:.1f}%**
    - **Total Units Sold:** {total_units:,}
    - **Total Records:** {len(df):,}
    - **Date Range:** {date_range}
    
    **Top Performers:**
    - **Best Revenue-Generating Region:** {top_region}
    - **Best Revenue-Generating Category:** {top_category}
    
    **💡 Next Steps:**
    Ask me specific questions about regional performance, monthly trends, profit margins, 
    campaign effectiveness, customer satisfaction, or inventory levels for deeper insights!
    """
    
    return {"text": text}


with st.sidebar:
    st.header("📁 Data Upload")
    uploaded_file = st.file_uploader("Choose your CSV file", type="csv")
    
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            
            if 'Date' in df.columns:
                df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
            
            numeric_columns = ['Revenue', 'Cost', 'Profit', 'Units_Sold', 'Customer_Satisfaction_Score', 'Inventory_Level']
            for col in numeric_columns:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            st.session_state.data = df
            
            st.success(f"✅ Data loaded successfully! Records: {len(df):,}")
            
            st.header("📊 Data Overview")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Total Records", f"{len(df):,}")
                if 'Revenue' in df.columns:
                    total_revenue = df['Revenue'].sum()
                    st.metric("Total Revenue", f"${total_revenue:,.0f}")
            
            with col2:
                if 'Date' in df.columns and not df['Date'].empty:
                    date_range = f"{df['Date'].min().strftime('%Y-%m-%d')} to {df['Date'].max().strftime('%Y-%m-%d')}"
                    st.write("**Date Range:**")
                    st.write(date_range)
                
                if 'Region' in df.columns:
                    regions = df['Region'].nunique()
                    st.metric("Regions", regions)
            
            st.subheader("🔍 Quick Insights")
            if 'Revenue' in df.columns and 'Region' in df.columns:
                top_region = df.groupby('Region')['Revenue'].sum().idxmax()
                st.caption(f"**Top Region:** {top_region}")
            
            if 'Revenue' in df.columns and 'Category_Department' in df.columns:
                top_category = df.groupby('Category_Department')['Revenue'].sum().idxmax()
                st.caption(f"**Top Category:** {top_category}")
            
        except Exception as e:
            st.error(f"Error loading file: {str(e)}")

if st.session_state.data is not None:
    st.header("💡 Quick Questions")
    col1, col2, col3 = st.columns(3)
    
    buttons = [
        ("📍 Regional Performance", "Show me revenue performance by region"),
        ("📈 Monthly Trends", "Show me monthly revenue trends"),
        ("💰 Profit Analysis", "Which products have the highest profit margins?"),
        ("🎯 Campaign Performance", "How do different campaigns perform?"),
        ("😊 Customer Satisfaction", "Show customer satisfaction analysis"),
        ("📦 Inventory Analysis", "Show inventory levels by category")
    ]
    
    if 'Region' in st.session_state.data.columns and 'Revenue' in st.session_state.data.columns:
        with col1:
            if st.button(buttons[0][0]):
                st.session_state.messages.append({"role": "user", "content": buttons[0][1]})
    
    if 'Date' in st.session_state.data.columns and 'Revenue' in st.session_state.data.columns:
        with col1:
            if st.button(buttons[1][0]):
                st.session_state.messages.append({"role": "user", "content": buttons[1][1]})

    if 'Profit' in st.session_state.data.columns and 'Revenue' in st.session_state.data.columns:
        with col2:
            if st.button(buttons[2][0]):
                st.session_state.messages.append({"role": "user", "content": buttons[2][1]})
    
    if 'Campaign_Name' in st.session_state.data.columns and 'Revenue' in st.session_state.data.columns:
        with col2:
            if st.button(buttons[3][0]):
                st.session_state.messages.append({"role": "user", "content": buttons[3][1]})
    
    if 'Customer_Satisfaction_Score' in st.session_state.data.columns:
        with col3:
            if st.button(buttons[4][0]):
                st.session_state.messages.append({"role": "user", "content": buttons[4][1]})
    
    if 'Inventory_Level' in st.session_state.data.columns and 'Category_Department' in st.session_state.data.columns:
        with col3:
            if st.button(buttons[5][0]):
                st.session_state.messages.append({"role": "user", "content": buttons[5][1]})


if st.session_state.data is not None:
    user_input = st.chat_input("Ask me anything about your data...")
    
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})

if st.session_state.messages:
    
    if st.session_state.messages[-1]["role"] == "user":
        latest_question = st.session_state.messages[-1]["content"]
        
        with st.spinner("Analyzing data..."):
            response = analyze_question(latest_question, st.session_state.data)
        
        st.session_state.messages.append({"role": "assistant", "content": response["text"], "chart": response.get("chart"), "dataframe": response.get("dataframe")})
        
        if "chart" in st.session_state.messages[-2]:
            del st.session_state.messages[-2]["chart"]
        if "dataframe" in st.session_state.messages[-2]:
            del st.session_state.messages[-2]["dataframe"]


    for message in st.session_state.messages:
        if message["role"] == "user":
            with st.chat_message("user"):
                st.write(message["content"])
        elif message["role"] == "assistant":
            with st.chat_message("assistant"):
                st.write(message["content"])
                
                if "chart" in message and message["chart"] is not None:
                    st.plotly_chart(message["chart"], use_container_width=True)
                
                if "dataframe" in message and message["dataframe"] is not None:
                    st.dataframe(message["dataframe"], use_container_width=True)


if st.session_state.data is None:
    st.info("👆 Please upload your CSV file in the sidebar to start analyzing your data!")
else:
    if len([m for m in st.session_state.messages if m["role"] != "user"]) == 0:
        st.session_state.messages.append({
            "role": "assistant", 
            "content": f"Great! I've loaded your data with {len(st.session_state.data):,} records. What would you like to analyze? You can use the **quick question buttons** above or ask me anything about your business performance data!"
        })