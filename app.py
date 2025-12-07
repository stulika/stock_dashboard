import gradio as gr
import pandas as pd
import yfinance as yf
from datetime import datetime
import plotly.graph_objs as go
from prophet import Prophet

# ---------- Technical Analysis ----------
def plot_stock_chart(file, chart_type):
    try:
        df = pd.read_excel(file, parse_dates=["Date"], index_col="Date", engine="openpyxl")

        if chart_type == "Buy/Sell Signal Chart":
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df.index, y=df["Close"], mode='lines', name='Close'))
            fig.add_trace(go.Scatter(x=df.index, y=df["Buy_Signal"], mode='markers', name='Buy', marker=dict(color='green', symbol='triangle-up', size=10)))
            fig.add_trace(go.Scatter(x=df.index, y=df["Sell_Signal"], mode='markers', name='Sell', marker=dict(color='red', symbol='triangle-down', size=10)))
            return fig, None

        elif chart_type == "RSI":
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df.index, y=df["momentum_rsi"], name="RSI"))
            fig.add_hline(y=70, line_dash="dash", line_color="red")
            fig.add_hline(y=30, line_dash="dash", line_color="green")
            return fig, None

        elif chart_type == "MACD":
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df.index, y=df["trend_macd"], name="MACD", line=dict(color="purple")))
            fig.add_trace(go.Scatter(x=df.index, y=df["trend_macd_signal"], name="Signal", line=dict(color="orange")))
            return fig, None

        elif chart_type == "Bollinger Bands":
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df.index, y=df["Close"], name="Close"))
            fig.add_trace(go.Scatter(x=df.index, y[df["volatility_bbm"]], name="Middle"))
            fig.add_trace(go.Scatter(x=df.index, y=df["volatility_bbh"], name="Upper"))
            fig.add_trace(go.Scatter(x=df.index, y=df["volatility_bbl"], name="Lower"))
            return fig, None

        elif chart_type == "Forecast (Prophet)":
            df_prophet = df[['Close']].reset_index()
            df_prophet.columns = ['ds', 'y']
            model = Prophet()
            model.fit(df_prophet)
            future = model.make_future_dataframe(periods=30)
            forecast = model.predict(future)

            fig = go.Figure()
            fig.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat'], name='Forecast'))
            fig.add_trace(go.Scatter(x=df_prophet['ds'], y=df_prophet['y'], name='Actual'))
            return fig, None

        elif chart_type == "Show Raw Data":
            return None, df.tail(50)

    except Exception as e:
        return None, f"❌ Error: {e}"

# ---------- Portfolio Tracker ----------
def analyze_portfolio(file):
    try:
        df = pd.read_excel(file, engine="openpyxl")
        df.columns = [str(col).strip() for col in df.columns]

        required_cols = {"Date", "Ticker", "Action", "Quantity", "Price"}
        if not required_cols.issubset(df.columns):
            return None, None, None, "❌ Missing columns: Date, Ticker, Action, Quantity, Price"

        df = df.dropna(subset=["Date", "Ticker", "Action", "Quantity", "Price"])
        df["Date"] = pd.to_datetime(df["Date"], errors='coerce')

        tickers = df["Ticker"].unique()
        all_data = pd.DataFrame()

        for ticker in tickers:
            data = yf.download(
                ticker,
                start=df["Date"].min().strftime('%Y-%m-%d'),
                end=datetime.today().strftime('%Y-%m-%d')
            )
            data["Ticker"] = ticker
            data["Date"] = data.index
            all_data = pd.concat([all_data, data[["Date", "Close", "Ticker"]]])

        merged = df.merge(all_data, on=["Date", "Ticker"], how="left")
        merged["Close"] = merged["Close"].fillna(method="ffill")

        merged["SignedQty"] = merged.apply(lambda row: row["Quantity"] if row["Action"] == "Buy" else -row["Quantity"], axis=1)
        merged["Investment"] = merged["Quantity"] * row["Price"]

        summary = merged.groupby("Ticker").agg({
            "SignedQty": "sum",
            "Investment": "sum"
        }).reset_index()

        summary["Current Price"] = summary["Ticker"].apply(lambda x: all_data[all_data["Ticker"] == x].iloc[-1]["Close"])
        summary["Current Value"] = summary["SignedQty"] * summary["Current Price"]
        summary["P&L"] = summary["Current Value"] - summary["Investment"]
        summary["P&L (%)"] = (summary["P&L"] / summary["Investment"]) * 100

        return summary, merged, df.tail(50), None

    except Exception as e:
        return None, None, None, f"❌ Portfolio error: {e}"

# ---------- Gradio UI ----------
with gr.Blocks() as demo:   #  FIXED: removed theme argument
    with gr.Tab("📈 Technical Analysis"):
        gr.Markdown("## 📊 Stock Technical Analysis")
        file = gr.File(label="📥 Upload Stock Excel File (.xlsx)")
        chart_type = gr.Dropdown(["Show Raw Data", "Buy/Sell Signal Chart", "RSI", "MACD", "Bollinger Bands", "Forecast (Prophet)"], label="Select Chart Type")
        btn = gr.Button("Submit")
        graph = gr.Plot()
        table = gr.Dataframe()

        btn.click(plot_stock_chart, inputs=[file, chart_type], outputs=[graph, table])

    with gr.Tab("💼 Portfolio Tracker"):
        gr.Markdown("## 💼 Portfolio Tracker & P&L Calculator")
        file2 = gr.File(label="📤 Upload Portfolio File (.xlsx)")
        submit2 = gr.Button("Analyze Portfolio")
        portfolio_summary = gr.Dataframe(label="📊 Portfolio Summary")
        trade_history = gr.Dataframe(label="📄 Trade History")
        raw_data = gr.Dataframe(label="🧾 Raw Uploaded Trades")
        msg = gr.Textbox(label="⚠️ Status")

        submit2.click(analyze_portfolio, inputs=file2, outputs=[portfolio_summary, trade_history, raw_data, msg])

demo.launch()
