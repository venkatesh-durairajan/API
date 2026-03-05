import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Portfolio Dashboard", layout="wide")

st.title("📊 My Investment Portfolio")

# -----------------------------
# Portfolio Holdings
# -----------------------------

portfolio = {
    "IOZ.AX": {"qty": 100, "buy_price": 28},
    "NDQ.AX": {"qty": 50, "buy_price": 30},
    "DHHF.AX": {"qty": 70, "buy_price": 26},
}

# -----------------------------
# Price Fetch Function
# -----------------------------

@st.cache_data(ttl=3600)
def get_stock_data(ticker):

    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="5d")

        if hist.empty:
            return 0, 0, 0

        price = hist["Close"].iloc[-1]

        if len(hist) > 1:
            prev = hist["Close"].iloc[-2]
            change = price - prev
            change_pct = (change / prev) * 100
        else:
            change = 0
            change_pct = 0

        return price, change, change_pct

    except:
        return 0, 0, 0


# -----------------------------
# Build Portfolio Table
# -----------------------------

data = []
total_invested = 0
total_current = 0

for ticker, info in portfolio.items():

    price, change, change_pct = get_stock_data(ticker)

    invested = info["qty"] * info["buy_price"]
    current = info["qty"] * price
    profit = current - invested

    total_invested += invested
    total_current += current

    data.append({
        "Ticker": ticker,
        "Qty": info["qty"],
        "Buy Price": info["buy_price"],
        "Current Price": round(price,2),
        "Daily Change": round(change,2),
        "Daily %": round(change_pct,2),
        "Invested": round(invested,2),
        "Current Value": round(current,2),
        "Profit/Loss": round(profit,2)
    })

df = pd.DataFrame(data)

# -----------------------------
# Display Portfolio Table
# -----------------------------

st.subheader("📈 Holdings")

st.dataframe(df, use_container_width=True)

# -----------------------------
# Portfolio Summary Metrics
# -----------------------------

st.subheader("📊 Portfolio Summary")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Invested", f"${total_invested:,.2f}")
col2.metric("Current Value", f"${total_current:,.2f}")

profit_total = total_current - total_invested
col3.metric("Profit / Loss", f"${profit_total:,.2f}")

return_pct = (profit_total / total_invested) * 100
col4.metric("Return %", f"{return_pct:.2f}%")

# -----------------------------
# Allocation Chart
# -----------------------------

st.subheader("🥧 Portfolio Allocation")

fig = px.pie(
    df,
    names="Ticker",
    values="Current Value",
)

st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# Portfolio Performance Chart
# -----------------------------

st.subheader("📉 Portfolio Trend (Last 3 Months)")

@st.cache_data(ttl=3600)
def get_portfolio_history():

    combined = pd.DataFrame()

    for ticker, info in portfolio.items():

        stock = yf.Ticker(ticker)
        hist = stock.history(period="3mo")

        hist["Value"] = hist["Close"] * info["qty"]

        if combined.empty:
            combined = hist[["Value"]]
        else:
            combined["Value"] += hist["Value"]

    return combined


history = get_portfolio_history()

fig2 = px.line(
    history,
    y="Value",
    title="Portfolio Value Over Time"
)

st.plotly_chart(fig2, use_container_width=True)

st.success("✅ Portfolio dashboard loaded successfully!")
