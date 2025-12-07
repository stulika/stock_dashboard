import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime

st.title("💼 Portfolio Tracker & P&L Calculator")

portfolio_file = st.file_uploader("📥 Upload Portfolio File (.xlsx)", type=["xlsx"])

if portfolio_file:
    try:
        # Try reading with single-level header
        try:
            trades = pd.read_excel(portfolio_file, parse_dates=["Date"])
        except ValueError:
            # Handle multi-level headers
            raw = pd.read_excel(portfolio_file, header=[0, 1])
            raw.columns = [col[0] if isinstance(col, tuple) else col for col in raw.columns]
            trades = raw.copy()

        trades.columns = [col.strip() for col in trades.columns]

        required = {"Date", "Ticker", "Action", "Quantity", "Price"}
        if not required.issubset(trades.columns):
            st.error("❌ Missing required columns: Date, Ticker, Action, Quantity, Price")
            st.stop()

        trades = trades.dropna(subset=["Date", "Ticker", "Action", "Quantity", "Price"])
        trades["Date"] = pd.to_datetime(trades["Date"])

        tickers = trades["Ticker"].unique()
        all_data = pd.DataFrame()

        for ticker in tickers:
            stock_data = yf.download(
                ticker,
                start=trades["Date"].min().strftime('%Y-%m-%d'),
                end=datetime.today().strftime('%Y-%m-%d')
            )
            stock_data["Ticker"] = ticker
            stock_data["Date"] = stock_data.index
            all_data = pd.concat([all_data, stock_data[["Date", "Close", "Ticker"]]])

        merged = trades.merge(all_data, on=["Date", "Ticker"], how="left")
        merged["Close"] = merged["Close"].fillna(method="ffill")

        merged["SignedQty"] = merged.apply(
            lambda row: row["Quantity"] if row["Action"].lower() == "buy" else -row["Quantity"], axis=1
        )
        merged["Investment"] = merged["Quantity"] * merged["Price"]

        summary = merged.groupby("Ticker").agg({
            "SignedQty": "sum",
            "Investment": "sum"
        }).reset_index()

        summary["Current Price"] = summary["Ticker"].apply(
            lambda x: all_data[all_data["Ticker"] == x].iloc[-1]["Close"]
        )
        summary["Current Value"] = summary["SignedQty"] * summary["Current Price"]
        summary["P&L"] = summary["Current Value"] - summary["Investment"]
        summary["P&L (%)"] = (summary["P&L"] / summary["Investment"]) * 100

        st.subheader("📊 Portfolio Summary")
        st.dataframe(summary.style.format({
            "Investment": "₹{:.2f}",
            "Current Price": "₹{:.2f}",
            "Current Value": "₹{:.2f}",
            "P&L": "₹{:.2f}",
            "P&L (%)": "{:.2f}%"
        }))

        st.subheader("📄 Trade History")
        st.dataframe(merged)

    except Exception as e:
        st.error(f"❌ Error reading portfolio: {e}")
else:
    st.info("👈 Upload your Excel portfolio file to get started.")
