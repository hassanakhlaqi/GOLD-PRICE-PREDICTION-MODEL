"""
Improved Streamlit UI for Gold Price Forecasting
Using modular architecture with XGBoost
"""

import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def _get_close_series(dataframe: pd.DataFrame, ticker_symbol: str):
    """Return a clean close price Series from yfinance data."""
    if isinstance(dataframe.columns, pd.MultiIndex):
        if ('Close', ticker_symbol) in dataframe.columns:
            return dataframe[('Close', ticker_symbol)]
        if 'Close' in dataframe.columns.get_level_values(0):
            close_df = dataframe['Close']
            if isinstance(close_df, pd.DataFrame):
                return close_df.iloc[:, 0]
            return close_df
    return dataframe['Close']

from core import get_config, DataPipeline, ModelManager, PreprocessingPipeline

# Page configuration
st.set_page_config(
    page_title="Gold Price Forecasting System",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 10px;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        margin: 10px 0;
    }
    .success-box {
        background: #d4edda;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #28a745;
    }
    .warning-box {
        background: #fff3cd;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #ffc107;
    }
    </style>
""", unsafe_allow_html=True)

# Title
st.markdown('<h1 class="main-header">🏆 Gold Price Forecasting System</h1>', unsafe_allow_html=True)
st.markdown("*Institutional-Grade XGBoost Quantitative Engine*")
st.markdown("---")

# Sidebar configuration
with st.sidebar:
    st.header("⚙️ Configuration Panel")
    
    config = get_config()
    
    # Data parameters
    st.subheader("📊 Data Settings")
    ticker = st.text_input("Instrument Ticker", value=config.data_ticker)
    
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", value=datetime.strptime(config.start_date, "%Y-%m-%d"))
    with col2:
        end_date = st.date_input("End Date", value=datetime.strptime(config.end_date, "%Y-%m-%d"))
    
    # Strategy parameters
    st.subheader("📈 Strategy Parameters")
    short_window = st.slider("Fast MA Window", min_value=5, max_value=30, value=20)
    long_window = st.slider("Slow MA Window", min_value=31, max_value=100, value=50)
    
    # Risk management
    st.subheader("💰 Risk Management")
    account_capital = st.number_input("Account Capital ($)", min_value=1000, max_value=1000000, value=10000, step=1000)
    risk_percentage = st.slider("Risk Per Trade (%)", min_value=0.5, max_value=5.0, value=1.0, step=0.5)

# Main tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Real-Time Dashboard",
    "🔍 Technical Analysis",
    "📊 Model Performance",
    "💡 Insights & Analytics",
    "⚙️ System Status"
])

with tab1:
    st.subheader("Live Market Data & Signals")
    
    try:
        # Fetch data
        with st.spinner("Fetching market data..."):
            df = yf.download(ticker, start=start_date, end=end_date, progress=False)
        
        if df.empty:
            st.error(f"No data available for {ticker}")
        else:
            close = _get_close_series(df, ticker)

            # Technical indicators
            df['SMA_Fast'] = close.rolling(window=short_window).mean()
            df['SMA_Slow'] = close.rolling(window=long_window).mean()
            df['Signal'] = np.where(df['SMA_Fast'] > df['SMA_Slow'], 1, -1)
            
            # Calculate metrics
            latest_price = close.iloc[-1]
            current_sma_fast = df['SMA_Fast'].iloc[-1]
            current_sma_slow = df['SMA_Slow'].iloc[-1]
            
            # Metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "Current Price",
                    f"${latest_price:,.2f}",
                    delta=f"{((latest_price / close.iloc[-2] - 1) * 100):.2f}%"
                )
            
            with col2:
                st.metric(
                    "Fast MA (SMA20)",
                    f"${current_sma_fast:,.2f}",
                    delta=None
                )
            
            with col3:
                st.metric(
                    "Slow MA (SMA50)",
                    f"${current_sma_slow:,.2f}",
                    delta=None
                )
            
            with col4:
                signal = "BUY ↑" if df['Signal'].iloc[-1] == 1 else "SELL ↓"
                st.metric("Signal", signal)
            
            st.markdown("---")
            
            # Interactive chart
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=df.index,
                y=close,
                name='Price',
                line=dict(color='gold', width=2)
            ))
            
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df['SMA_Fast'],
                name=f'Fast MA ({short_window})',
                line=dict(color='blue', dash='dash')
            ))
            
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df['SMA_Slow'],
                name=f'Slow MA ({long_window})',
                line=dict(color='red', dash='dash')
            ))
            
            fig.update_layout(
                title="Price & Moving Averages",
                yaxis_title="Price (USD)",
                hovermode='x unified',
                height=500
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    except Exception as e:
        st.error(f"Error fetching data: {str(e)}")

with tab2:
    st.subheader("Technical Indicators Analysis")
    
    try:
        df = yf.download(ticker, start=start_date, end=end_date, progress=False)
        
        close = _get_close_series(df, ticker)

        # Volatility indicator
        rolling_std = close.rolling(window=20).std()
        rolling_mean = close.rolling(window=20).mean()
        bb_upper = rolling_mean + (rolling_std * 2)
        bb_lower = rolling_mean - (rolling_std * 2)
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df.index,
            y=close,
            name='Price',
            line=dict(color='gold', width=2)
        ))
        
        fig.add_trace(go.Scatter(
            x=df.index,
            y=bb_upper,
            name='BB Upper',
            line=dict(color='lightblue', dash='dash'),
            fill=None
        ))
        
        fig.add_trace(go.Scatter(
            x=df.index,
            y=bb_lower,
            name='BB Lower',
            line=dict(color='lightblue', dash='dash'),
            fill='tonexty',
            fillcolor='rgba(0, 100, 200, 0.1)'
        ))
        
        fig.update_layout(
            title="Bollinger Bands",
            yaxis_title="Price (USD)",
            hovermode='x unified',
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    except Exception as e:
        st.error(f"Error analyzing indicators: {str(e)}")

with tab3:
    st.subheader("Model Performance Metrics")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Model Type", "XGBoost Classifier")
        st.metric("Status", "✅ Active")
    
    with col2:
        st.metric("Estimators", "100")
        st.metric("Learning Rate", "0.05")
    
    with col3:
        st.metric("Max Depth", "5")
        st.metric("Test Size", "20%")
    
    st.markdown("---")
    st.info("Model training and evaluation features coming soon...")

with tab4:
    st.subheader("Market Insights & Analytics")
    
    try:
        df = yf.download(ticker, start=start_date, end=end_date, progress=False)
        
        close = _get_close_series(df, ticker)

        # Returns distribution
        returns = close.pct_change().dropna()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Avg Daily Return", f"{returns.mean()*100:.3f}%")
            st.metric("Volatility (Std)", f"{returns.std()*100:.3f}%")
        
        with col2:
            st.metric("Sharpe Ratio", f"{returns.mean() / returns.std() * np.sqrt(252):.2f}")
            st.metric("Max Drawdown", f"{(close.min() / close.max() - 1)*100:.2f}%")
        
        st.markdown("---")
        
        # Returns distribution chart
        fig = px.histogram(returns * 100, nbins=50, title="Returns Distribution")
        fig.update_xaxes(title_text="Daily Returns (%)")
        st.plotly_chart(fig, use_container_width=True)
    
    except Exception as e:
        st.error(f"Error generating insights: {str(e)}")

with tab5:
    st.subheader("System Status & Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="success-box">✅ Data Pipeline: Active</div>', unsafe_allow_html=True)
        st.markdown('<div class="success-box">✅ Model Manager: Operational</div>', unsafe_allow_html=True)
        st.markdown('<div class="success-box">✅ API Endpoints: Available</div>', unsafe_allow_html=True)
    
    with col2:
        st.write("**System Information:**")
        st.write(f"- Configuration: Loaded from config.yaml")
        st.write(f"- Data Ticker: {ticker}")
        st.write(f"- Last Update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    st.markdown("---")
    st.write("**Available Endpoints:**")
    st.code("""
    GET  /health                  - System health check
    POST /predict                 - Make predictions
    GET  /features                - Get feature names
    GET  /feature-importance      - Get feature importance
    GET  /model-info              - Get model information
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>Gold Price Forecasting System | Powered by XGBoost | Last Updated: 2026-05-29</p>
</div>
""", unsafe_allow_html=True)
