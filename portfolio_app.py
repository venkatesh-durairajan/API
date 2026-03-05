import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
import json
import os

st.title("📊 My Personal Portfolio Dashboard")

FILE_NAME = "portfolio.json"

# Load saved portfolio
if os.path.exists(FILE_NAME):
    with open(FILE_NAME, "r") as f:
        portfolio = json.load(f)
else:
    portfolio = {}

# Function to save portfolio
def save_portfolio():
    with open(FILE_NAME, "w") as f:
        json.dump(portfolio, f)

# Get stock price (cached to avoid Yahoo limits)
@st.cache_data(ttl=3600)
def get_price(ticker):
    stock = yf.Ticker(ticker)
    data = stock.history(period="5d")
    if len(data) == 0:
        return 0
    return data["Close"].iloc[-1]

# Sidebar input to add stocks
st.sidebar.header("➕ Add Stock / ETF")

ticker = st.sidebar.text_input("Ticker (Example: NDQ.AX)")
qty = st.sidebar.number_input("Quantity", min_value=1)
buy_price = st.sidebar.number_input("Buy Price", min_value=0.0)

if st.sidebar.button("Add to Portfolio"):
    if ticker:
        portfolio[ticker.upper()] = {
            "qty": qty,
            "buy_price": buy_price
        }
        save_portfolio()
        st.sidebar.success("Added successfully!")

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

st.subheader("📊 Portfolio Summary")

st.metric("Total Invested", f"${round(total_invested,2)}")
st.metric("Current Value", f"${round(total_current,2)}")
st.metric("Total Profit/Loss", f"${round(total_current-total_invested,2)}")

# Allocation chart
if len(df) > 0:
    fig = px.pie(df, names="Ticker", values="Current Value", title="Portfolio Allocation")
    st.plotly_chart(fig)
