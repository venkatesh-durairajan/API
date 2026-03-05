import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px
import os

st.set_page_config(page_title="My Portfolio", layout="wide")

st.title("📊 My Personal Portfolio Dashboard")

FILE = "portfolio.csv"

# ---------- Load Portfolio ----------
if os.path.exists(FILE):
    df = pd.read_csv(FILE)
else:
    df = pd.DataFrame(columns=["Ticker","Qty","Buy Price"])

# ---------- Function to Get Price ----------
@st.cache_data(ttl=3600)
def get_price(ticker):
    try:
        data = yf.Ticker(ticker).history(period="2d")
        return data["Close"].iloc[-1]
    except:
        return None


# ---------- Add Stock ----------
st.sidebar.header("➕ Add Stock")

ticker = st.sidebar.text_input("Ticker (Example: NDQ.AX)")
qty = st.sidebar.number_input("Quantity", min_value=1)
buy_price = st.sidebar.number_input("Buy Price", min_value=0.0)

if st.sidebar.button("Add Stock"):

    new_row = pd.DataFrame([[ticker.upper(), qty, buy_price]],
                           columns=["Ticker","Qty","Buy Price"])

    df = pd.concat([df, new_row], ignore_index=True)

    df.to_csv(FILE, index=False)

    st.sidebar.success("Stock Added!")

# ---------- Delete Stock ----------
st.sidebar.header("❌ Delete Stock")

if not df.empty:
    delete_ticker = st.sidebar.selectbox("Select stock", df["Ticker"])

    if st.sidebar.button("Delete"):

        df = df[df["Ticker"] != delete_ticker]

        df.to_csv(FILE, index=False)

        st.sidebar.success("Deleted!")


# ---------- Portfolio Calculation ----------
data = []

total_invested = 0
total_current = 0

for index,row in df.iterrows():

    ticker = row["Ticker"]
    qty = row["Qty"]
    buy_price = row["Buy Price"]

    price = get_price(ticker)

    if price is None:
        continue

    invested = qty * buy_price
    current = qty * price
    profit = current - invested

    total_invested += invested
    total_current += current

    data.append({
        "Ticker": ticker,
        "Qty": qty,
        "Buy Price": buy_price,
        "Current Price": round(price,2),
        "Invested": round(invested,2),
        "Current Value": round(current,2),
        "Profit/Loss": round(profit,2)
    })

portfolio_df = pd.DataFrame(data)

# ---------- Show Portfolio ----------
st.subheader("📈 Portfolio Holdings")
st.dataframe(portfolio_df, use_container_width=True)

# ---------- Summary ----------
st.subheader("📊 Portfolio Summary")

col1,col2,col3 = st.columns(3)

col1.metric("Total Invested", f"${total_invested:,.2f}")
col2.metric("Current Value", f"${total_current:,.2f}")
col3.metric("Profit/Loss", f"${total_current-total_invested:,.2f}")

# ---------- Allocation Chart ----------
if not portfolio_df.empty:

    fig = px.pie(portfolio_df,
                 names="Ticker",
                 values="Current Value",
                 title="Portfolio Allocation")

    st.plotly_chart(fig, use_container_width=True)
