import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="My Portfolio", layout="wide")

st.title("📈 My Stock Portfolio")

# -----------------------------
# SESSION STORAGE
# -----------------------------

if "portfolio" not in st.session_state:
    st.session_state.portfolio = pd.DataFrame(columns=[
        "Ticker", "Shares", "Buy Price"
    ])


# -----------------------------
# GET STOCK PRICE
# -----------------------------

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


# -----------------------------
# ADD STOCK
# -----------------------------

st.subheader("Add Stock")

col1, col2, col3 = st.columns(3)

with col1:
    ticker = st.text_input("Ticker (Example: AAPL or CBA.AX)")

with col2:
    shares = st.number_input("Shares", min_value=0.0, step=1.0)

with col3:
    price = st.number_input("Buy Price", min_value=0.0, step=0.1)

if st.button("Add Stock"):

    if ticker != "":

        new_row = pd.DataFrame({
            "Ticker": [ticker.upper()],
            "Shares": [shares],
            "Buy Price": [price]
        })

        st.session_state.portfolio = pd.concat(
            [st.session_state.portfolio, new_row],
            ignore_index=True
        )

        st.success("Stock added successfully")


# -----------------------------
# PORTFOLIO TABLE
# -----------------------------

st.subheader("Portfolio")

portfolio = st.session_state.portfolio

rows = []

total_invested = 0
total_value = 0

for i, row in portfolio.iterrows():

    ticker = row["Ticker"]
    shares = float(row["Shares"])
    buy_price = float(row["Buy Price"])

    price = get_price(ticker)

    invested = shares * buy_price

    if price:
        value = shares * price
    else:
        value = 0

    profit = value - invested

    total_invested += invested
    total_value += value

    rows.append({
        "Ticker": ticker,
        "Shares": shares,
        "Buy Price": buy_price,
        "Current Price": price,
        "Invested": invested,
        "Value": value,
        "Profit": profit
    })

    col1, col2, col3, col4, col5 = st.columns([2,2,2,1,1])

    with col1:
        st.write(f"**{ticker}**")

    with col2:
        st.write(f"Shares: {shares}")

    with col3:
        st.write(f"Buy: ${buy_price}")

    with col4:
        if st.button("Delete", key=f"del{i}"):
            st.session_state.portfolio = portfolio.drop(i).reset_index(drop=True)
            st.rerun()

    with col5:
        if price:
            st.write(f"Price: ${round(price,2)}")
        else:
            st.write("Price: N/A")


# -----------------------------
# SUMMARY
# -----------------------------

st.subheader("Summary")

profit_total = total_value - total_invested

c1, c2, c3 = st.columns(3)

with c1:
    st.metric("Invested", f"${round(total_invested,2)}")

with c2:
    st.metric("Value", f"${round(total_value,2)}")

with c3:
    st.metric("Profit/Loss", f"${round(profit_total,2)}")


# -----------------------------
# PIE CHART
# -----------------------------

if len(rows) > 0:

    df = pd.DataFrame(rows)

    fig = px.pie(
        df,
        names="Ticker",
        values="Value",
        title="Portfolio Allocation"
    )

    st.plotly_chart(fig, width='stretch')
