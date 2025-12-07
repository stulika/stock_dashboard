📈 Stock Analysis & Portfolio Tracker Dashboard

A modern, interactive stock market analysis tool built using **Streamlit**, **Gradio**, and **Python**. This dashboard lets users explore technical indicators, analyze market trends, generate forecasts, track portfolio performance, and download insights — all in one place.
🚀 Features

📊 Technical Analysis
* RSI, MACD, Bollinger Bands
* Candlestick charts
* Buy/Sell signal visualization
* Multi-stock comparison

🔮 Forecasting (Prophet)
* 7/30/90-day price predictions
* Trend & seasonality insights

📁 Data Inputs
* Upload Excel/CSV
* Live data fetch via yfinance
* Auto-cleaning & validation

🧮 Portfolio Tools
* Track multiple stocks
* Calculate overall returns
* Risk–reward summary

🛠️ Dual UI Support
* **Streamlit Dashboard**
* **Gradio App** (minimal, fast, shareable)

🧰 Tech Stack
* **Python**
* **Streamlit & Gradio**
* **yFinance**
* **Prophet**
* **Plotly**

📂 Project Structure

```
stock-analysis-dashboard/
│── streamlit_app.py
│── gradio_app.py
│── indicators/
│   ├── rsi.py
│   ├── macd.py
│   ├── bollinger.py
│── utils/
│── data/
│── requirements.txt
│── README.md
│── .gitignore
```

---

🛠️ Installation

1️⃣ Clone the repository

```bash
git clone https://github.com/your-username/stock-analysis-dashboard.git
cd stock-analysis-dashboard
```

2️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

---

 ▶️ Running the Dashboard

**Streamlit Version**

```bash
streamlit run streamlit_app.py
```

**Gradio Version**

```bash
python gradio_app.py
```

---

💡 Future Enhancements

* Automated alerts (email/WhatsApp)
* Sentiment analysis (Twitter/News)
* Portfolio optimization (Markowitz model)
* Multi-timeframe indicator support

🤝 Contributors

**Tulika Sharma**


Just say **“enhance the README”**.
