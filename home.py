# Home.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from prophet import Prophet
from prophet.plot import plot_plotly
import plotly.graph_objs as go


st.set_page_config(page_title="Stock Dashboard", layout="wide")

# Upload technical analysis Excel files
uploaded_files = st.sidebar.file_uploader("📤 Upload stock Excel files", type=["xlsx"], accept_multiple_files=True)

# Load data
stock_data = {}
if uploaded_files:
    for file in uploaded_files:
        try:
            df = pd.read_excel(file, parse_dates=["Date"], index_col="Date", engine="openpyxl")
            stock_data[file.name] = df
        except Exception as e:
            st.sidebar.error(f"Failed to read {file.name}: {e}")

if not stock_data:
    st.warning("👈 Please upload one or more Excel files to begin.")
    st.stop()

selected_stock = st.sidebar.selectbox("📈 Choose a Stock", list(stock_data.keys()))
df = stock_data[selected_stock]
st.title(f"📊 {selected_stock.replace('.xlsx', '')} Stock Dashboard")

# View selector
option = st.sidebar.selectbox(
    "Choose Analysis View",
    ["📉 Buy/Sell Signal Chart", "📈 RSI Chart", "📈 MACD Chart", "📈 Bollinger Bands Chart", "🧾 Show Raw Data", "🔮 Forecast Closing Price (Prophet)"]
)

# Plotting blocks
if option == "📉 Buy/Sell Signal Chart":
    st.subheader("Buy/Sell Signals")
    fig, ax = plt.subplots(figsize=(14, 5))
    ax.plot(df['Close'], label='Close', color='blue')
    ax.scatter(df.index, df['Buy_Signal'], label='Buy', marker='^', color='green', s=100)
    ax.scatter(df.index, df['Sell_Signal'], label='Sell', marker='v', color='red', s=100)
    ax.legend()
    st.pyplot(fig)

elif option == "📈 RSI Chart":
    st.subheader("RSI")
    fig, ax = plt.subplots(figsize=(14, 4))
    ax.plot(df['momentum_rsi'], label='RSI')
    ax.axhline(70, linestyle='--', color='red')
    ax.axhline(30, linestyle='--', color='green')
    ax.legend()
    st.pyplot(fig)

elif option == "📈 MACD Chart":
    st.subheader("MACD")
    fig, ax = plt.subplots(figsize=(14, 4))
    ax.plot(df['trend_macd'], label='MACD', color='purple')
    ax.plot(df['trend_macd_signal'], label='Signal Line', color='orange')
    ax.axhline(0, linestyle='--')
    ax.legend()
    st.pyplot(fig)

elif option == "📈 Bollinger Bands Chart":
    st.subheader("Bollinger Bands")
    if all(col in df.columns for col in ['Close', 'volatility_bbm', 'volatility_bbh', 'volatility_bbl']):
        fig, ax = plt.subplots(figsize=(14, 5))
        ax.plot(df['Close'], label='Close', color='blue')
        ax.plot(df['volatility_bbm'], label='Middle Band', linestyle='--')
        ax.plot(df['volatility_bbh'], label='Upper Band', linestyle='--')
        ax.plot(df['volatility_bbl'], label='Lower Band', linestyle='--')
        ax.legend()
        st.pyplot(fig)
    else:
        st.error("Bollinger Band columns not found.")

elif option == "🧾 Show Raw Data":
    st.subheader("Raw Data")
    st.dataframe(df.tail(50))

elif option == "🔮 Forecast Closing Price (Prophet)":
    st.subheader("🔮 Prophet Forecast")
    df_prophet = df[['Close']].reset_index()
    df_prophet.columns = ["ds", "y"]
    try:
        model = Prophet()
        model.fit(df_prophet)
        future = model.make_future_dataframe(periods=30)
        forecast = model.predict(future)
        fig1 = plot_plotly(model, forecast)
        st.plotly_chart(fig1, use_container_width=True)
        st.dataframe(forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]].tail(30))
    except Exception as e:
        st.error(f"Forecasting failed: {e}")
