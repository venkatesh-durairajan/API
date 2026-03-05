import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
import numpy as np

st.set_page_config(page_title="My Portfolio", layout="wide")

st.title("📈 My Personal Portfolio Dashboard")

# -------------------------
# SESSION STORAGE
# -------------------------

if "portfolio" not in st.session_state:
    st.session_state.portfolio = pd.DataFrame(columns=[
        "Ticker", "Shares", "Buy Price"
    ])

# -------------------------
# GET STOCK PRICE
# -------------------------

@st.cache_data(ttl=300)
def get_price(ticker):

    try:
        stock = yf.Ticker(ticker)
        price = stock.fast_info.get("lastPrice")

        if price:
            return float(price)

        hist = stock.history(period="5d")

        if not hist.empty:
            return float(hist["Close"].iloc[-1])

        return None

    except:
        return None


# -------------------------
# ADD STOCK
# -------------------------

st.subheader("Add Stock")

c1, c2, c3 = st.columns(3)

with c1:
    ticker = st.text_input("Ticker")

with c2:
    shares = st.number_input("Shares", min_value=0.0)

with c3:
    buy_price = st.number_input("Buy Price", min_value=0.0)

if st.button("Add Stock"):

    if ticker != "":

        new_row = pd.DataFrame({
            "Ticker":[ticker.upper()],
            "Shares":[shares],
            "Buy Price":[buy_price]
        })

        st.session_state.portfolio = pd.concat(
            [st.session_state.portfolio,new_row],
            ignore_index=True
        )

        st.success("Stock added")


# -------------------------
# PORTFOLIO
# -------------------------

st.subheader("📊 Portfolio")

portfolio = st.session_state.portfolio

data = []

total_invested = 0
total_value = 0

for i,row in portfolio.iterrows():

    ticker = row["Ticker"]
    shares = float(row["Shares"])
    buy = float(row["Buy Price"])

    price = get_price(ticker)

    invested = shares * buy

    if price:
        value = shares * price
    else:
        value = 0

    profit = value - invested

    total_invested += invested
    total_value += value

    data.append({
        "Ticker":ticker,
        "Shares":shares,
        "Buy":buy,
        "Current":price,
        "Invested":invested,
        "Value":value,
        "Profit":profit
    })

df = pd.DataFrame(data)

st.dataframe(df, width='stretch')


# -------------------------
# SUMMARY
# -------------------------

st.subheader("💰 Summary")

profit = total_value - total_invested

c1,c2,c3 = st.columns(3)

c1.metric("Invested", f"${total_invested:,.2f}")
c2.metric("Value", f"${total_value:,.2f}")
c3.metric("Profit/Loss", f"${profit:,.2f}")


# -------------------------
# PIE CHART
# -------------------------

if len(df)>0:

    fig = px.pie(
        df,
        names="Ticker",
        values="Value",
        title="Portfolio Allocation"
    )

    st.plotly_chart(fig, width='stretch')


# -------------------------
# PORTFOLIO HISTORY
# -------------------------

st.subheader("📈 Portfolio Growth")

if len(portfolio)>0:

    history_values = []

    for ticker in portfolio["Ticker"]:

        stock = yf.Ticker(ticker)
        hist = stock.history(period="1y")

        history_values.append(hist["Close"])

    combined = pd.concat(history_values, axis=1)

    combined.columns = portfolio["Ticker"]

    portfolio_history = combined.sum(axis=1)

    chart_df = pd.DataFrame({
        "Date":portfolio_history.index,
        "Value":portfolio_history.values
    })

    fig2 = px.line(chart_df, x="Date", y="Value")

    st.plotly_chart(fig2, width='stretch')


# -------------------------
# MARKET DASHBOARD
# -------------------------

st.subheader("🌍 Market Overview")

markets = {
    "S&P 500":"^GSPC",
    "NASDAQ":"^IXIC",
    "ASX200":"^AXJO",
    "Bitcoin":"BTC-USD"
}

m1,m2,m3,m4 = st.columns(4)

cols=[m1,m2,m3,m4]

for (name,ticker),col in zip(markets.items(),cols):

    price = get_price(ticker)

    if price:
        col.metric(name, round(price,2))
