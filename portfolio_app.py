import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="My Portfolio", layout="wide")

st.title("📈 My Portfolio Dashboard")

DATA_FILE = "portfolio.csv"

# --------------------------
# LOAD DATA
# --------------------------

if os.path.exists(DATA_FILE):
    portfolio = pd.read_csv(DATA_FILE)
else:
    portfolio = pd.DataFrame(columns=["Ticker","Shares","Buy Price"])

# --------------------------
# GET PRICE
# --------------------------

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


# --------------------------
# ADD STOCK
# --------------------------

st.subheader("Add Stock")

c1,c2,c3 = st.columns(3)

with c1:
    ticker = st.text_input("Ticker (Example: NDQ.AX)")

with c2:
    shares = st.number_input("Shares",min_value=0.0)

with c3:
    buy = st.number_input("Buy Price",min_value=0.0)

if st.button("Add Stock"):

    if ticker != "":

        new_row = pd.DataFrame({
            "Ticker":[ticker.upper()],
            "Shares":[shares],
            "Buy Price":[buy]
        })

        portfolio = pd.concat([portfolio,new_row],ignore_index=True)

        portfolio.to_csv(DATA_FILE,index=False)

        st.success("Stock added successfully!")

# --------------------------
# PORTFOLIO TABLE
# --------------------------

st.subheader("📊 Portfolio")

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

st.dataframe(df,width='stretch')

# --------------------------
# SUMMARY
# --------------------------

st.subheader("💰 Summary")

profit = total_value-total_invested

c1,c2,c3 = st.columns(3)

c1.metric("Invested",f"${total_invested:,.2f}")
c2.metric("Value",f"${total_value:,.2f}")
c3.metric("Profit/Loss",f"${profit:,.2f}")

# --------------------------
# PIE CHART
# --------------------------

if len(df)>0:

    fig = px.pie(df,names="Ticker",values="Value",title="Portfolio Allocation")

    st.plotly_chart(fig,width='stretch')
