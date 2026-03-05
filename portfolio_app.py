import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px

st.title("📊 My Personal Portfolio Dashboard")

# Portfolio holdings
portfolio = {
    "IOZ.AX": {"qty": 100, "buy_price": 28},
    "NDQ.AX": {"qty": 50, "buy_price": 30},
    "DHHF.AX": {"qty": 70, "buy_price": 26},
}

# Function to fetch stock data
@st.cache_data(ttl=3600)
def get_stock_data(ticker):
    stock = yf.Ticker(ticker)
    hist = stock.history(period="2d")

    price = hist["Close"].iloc[-1]
    prev = hist["Close"].iloc[-2]

    change = price - prev
    change_pct = (change / prev) * 100

    return price, change, change_pct


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
        "Current Price": round(price, 2),
        "Daily Change": round(change, 2),
        "Daily %": round(change_pct, 2),
        "Invested": round(invested, 2),
        "Current Value": round(current, 2),
        "Profit/Loss": round(profit, 2)
    })


df = pd.DataFrame(data)

st.subheader("📈 Portfolio Holdings")
st.dataframe(df, use_container_width=True)

# Portfolio Summary
st.subheader("📊 Portfolio Summary")

col1, col2, col3 = st.columns(3)

col1.metric("Total Invested", f"${total_invested:,.2f}")
col2.metric("Current Value", f"${total_current:,.2f}")
col3.metric("Profit / Loss", f"${(total_current-total_invested):,.2f}")

# Return %
return_pct = ((total_current - total_invested) / total_invested) * 100
st.metric("Portfolio Return %", f"{return_pct:.2f}%")

# Allocation Pie Chart
st.subheader("📊 Portfolio Allocation")

fig = px.pie(
    df,
    names="Ticker",
    values="Current Value",
    title="Portfolio Allocation"
)

st.plotly_chart(fig, use_container_width=True)
