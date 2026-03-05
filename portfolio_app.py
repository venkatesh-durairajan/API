import streamlit as st
import yfinance as yf
import pandas as pd
import os

st.set_page_config(page_title="My Portfolio Tracker", layout="wide")

FILE = "portfolio.csv"

# ---------------------------
# Load portfolio
# ---------------------------
def load_portfolio():
    if os.path.exists(FILE):
        return pd.read_csv(FILE)
    else:
        return pd.DataFrame(columns=["Ticker", "Shares", "Buy Price"])

# ---------------------------
# Save portfolio
# ---------------------------
def save_portfolio(df):
    df.to_csv(FILE, index=False)

# ---------------------------
# Get stock data safely
# ---------------------------
@st.cache_data(ttl=300)
def get_stock_data(ticker):

    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="5d")

        if hist.empty or len(hist) < 2:
            return None, None, None

        price = hist["Close"].iloc[-1]
        prev = hist["Close"].iloc[-2]

        change = price - prev
        change_pct = (change / prev) * 100

        return price, change, change_pct

    except:
        return None, None, None


# ---------------------------
# Load data
# ---------------------------
portfolio = load_portfolio()

st.title("📊 Personal Portfolio Tracker")

# ---------------------------
# Add Stock
# ---------------------------
st.subheader("Add Stock")

col1, col2, col3 = st.columns(3)

with col1:
    ticker = st.text_input("Ticker (Example: AAPL or CBA.AX)")

with col2:
    shares = st.number_input("Shares", min_value=0.0, step=1.0)

with col3:
    buy_price = st.number_input("Buy Price", min_value=0.0)

if st.button("Add Stock"):

    if ticker != "" and shares > 0:
        new_row = pd.DataFrame([[ticker.upper(), shares, buy_price]],
                               columns=["Ticker", "Shares", "Buy Price"])

        portfolio = pd.concat([portfolio, new_row], ignore_index=True)
        save_portfolio(portfolio)

        st.success("Stock added successfully")
        st.rerun()


# ---------------------------
# Portfolio Table
# ---------------------------
st.subheader("My Portfolio")

if len(portfolio) == 0:
    st.info("No stocks added yet")

else:

    total_value = 0
    total_cost = 0

    for i, row in portfolio.iterrows():

        ticker = row["Ticker"]
        shares = row["Shares"]
        buy_price = row["Buy Price"]

        price, change, change_pct = get_stock_data(ticker)

        col1, col2, col3, col4, col5, col6 = st.columns([2,2,2,2,1,1])

        with col1:
            st.write(f"**{ticker}**")

        with col2:
            st.write(f"Shares: {shares}")

        with col3:
            st.write(f"Buy: ${buy_price}")

        with col4:
            if price:
                st.write(f"Price: ${round(price,2)}")
            else:
                st.write("Price: N/A")

        with col5:
            if st.button("Edit", key=f"edit{i}"):
                st.session_state["edit_index"] = i

        with col6:
            if st.button("Delete", key=f"delete{i}"):

                portfolio = portfolio.drop(i)
                portfolio = portfolio.reset_index(drop=True)

                save_portfolio(portfolio)

                st.success("Deleted")
                st.rerun()

        if price:
            total_value += price * shares
            total_cost += buy_price * shares


# ---------------------------
# Edit Stock
# ---------------------------
if "edit_index" in st.session_state:

    idx = st.session_state["edit_index"]

    st.subheader("Edit Stock")

    row = portfolio.loc[idx]

    new_shares = st.number_input("Shares", value=float(row["Shares"]))
    new_price = st.number_input("Buy Price", value=float(row["Buy Price"]))

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Save Changes"):

            portfolio.at[idx, "Shares"] = new_shares
            portfolio.at[idx, "Buy Price"] = new_price

            save_portfolio(portfolio)

            del st.session_state["edit_index"]

            st.success("Updated")
            st.rerun()

    with col2:
        if st.button("Cancel"):

            del st.session_state["edit_index"]
            st.rerun()


# ---------------------------
# Portfolio Summary
# ---------------------------
if len(portfolio) > 0:

    st.subheader("Portfolio Summary")

    profit = total_value - total_cost

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Invested", f"${round(total_cost,2)}")
    col2.metric("Current Value", f"${round(total_value,2)}")
    col3.metric("Profit / Loss", f"${round(profit,2)}")
