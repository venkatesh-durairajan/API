import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px

st.title("📊 My Personal Portfolio Dashboard")

# Cache price to avoid Yahoo rate limit
@st.cache_data(ttl=3600)
def get_price(ticker):
    stock = yf.Ticker(ticker)
    data = stock.history(period="1d")
    return data["Close"].iloc[-1]

# Your holdings (Edit anytime)
portfolio = {
    "IOZ.AX": {"qty": 100, "buy_price": 28},
    "NDQ.AX": {"qty": 50, "buy_price": 30},
    "DHHF.AX": {"qty": 70, "buy_price": 26},
}

data = []
total_invested = 0
total_current = 0

for ticker, info in portfolio.items():

    price = get_price(ticker)

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
        "Invested": round(invested,2),
        "Current Value": round(current,2),
        "Profit/Loss": round(profit,2)
    })

df = pd.DataFrame(data)

st.subheader("📈 Portfolio Holdings")
st.dataframe(df)

st.subheader("📊 Summary")
st.write("Total Invested:", round(total_invested,2))
st.write("Current Value:", round(total_current,2))
st.write("Total Profit/Loss:", round(total_current - total_invested,2))

# Pie Chart
fig = px.pie(df, names="Ticker", values="Current Value", title="Portfolio Allocation")
st.plotly_chart(fig)
