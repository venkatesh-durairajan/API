import streamlit as st
import yfinance as yf
import pandas as pd
import os

st.set_page_config(page_title="Portfolio Tracker", layout="wide")

FILE = "portfolio.csv"

# -----------------------------------
# Load Portfolio (Fix missing columns)
# -----------------------------------
def load_portfolio():

    if os.path.exists(FILE):
        df = pd.read_csv(FILE)

        required_cols = ["Ticker", "Shares", "Buy Price"]

        for col in required_cols:
            if col not in df.columns:
                df[col] = 0

        df = df[required_cols]

    else:
        df = pd.DataFrame(columns=["Ticker","Shares","Buy Price"])

    return df


# -----------------------------------
# Save Portfolio
# -----------------------------------
def save_portfolio(df):
    df.to_csv(FILE,index=False)


# -----------------------------------
# Get Stock Price
# -----------------------------------
@st.cache_data(ttl=300)
def get_price(ticker):

    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="5d")

        if hist.empty:
            return None

        return hist["Close"].iloc[-1]

    except:
        return None


# -----------------------------------
# Load data
# -----------------------------------
portfolio = load_portfolio()

st.title("📈 My Portfolio")

# -----------------------------------
# Add Stock
# -----------------------------------
st.subheader("Add Stock")

col1,col2,col3 = st.columns(3)

ticker = col1.text_input("Ticker (Example: AAPL or CBA.AX)")
shares = col2.number_input("Shares",min_value=0.0)
buy_price = col3.number_input("Buy Price",min_value=0.0)

if st.button("Add"):

    if ticker:

        new_row = pd.DataFrame({
            "Ticker":[ticker.upper()],
            "Shares":[shares],
            "Buy Price":[buy_price]
        })

        portfolio = pd.concat([portfolio,new_row],ignore_index=True)

        save_portfolio(portfolio)

        st.success("Stock added")

        st.rerun()


# -----------------------------------
# Portfolio Table
# -----------------------------------
st.subheader("Portfolio")

total_value = 0
total_cost = 0

for i,row in portfolio.iterrows():

    ticker = row.get("Ticker","")
    shares = float(row.get("Shares",0))
    buy_price = float(row.get("Buy Price",0))

    price = get_price(ticker)

    c1,c2,c3,c4,c5,c6 = st.columns([2,2,2,2,1,1])

    c1.write(f"**{ticker}**")
    c2.write(f"Shares: {shares}")
    c3.write(f"Buy: ${buy_price}")

    if price:
        c4.write(f"Price: ${round(price,2)}")
    else:
        c4.write("Price: N/A")

    if c5.button("Edit",key=f"edit{i}"):
        st.session_state.edit_index = i

    if c6.button("Delete",key=f"del{i}"):

        portfolio = portfolio.drop(i).reset_index(drop=True)

        save_portfolio(portfolio)

        st.rerun()

    if price:
        total_value += price * shares
        total_cost += buy_price * shares


# -----------------------------------
# Edit Stock
# -----------------------------------
if "edit_index" in st.session_state:

    idx = st.session_state.edit_index

    st.subheader("Edit Stock")

    row = portfolio.loc[idx]

    new_shares = st.number_input("New Shares",value=float(row["Shares"]))
    new_price = st.number_input("New Buy Price",value=float(row["Buy Price"]))

    if st.button("Save"):

        portfolio.at[idx,"Shares"] = new_shares
        portfolio.at[idx,"Buy Price"] = new_price

        save_portfolio(portfolio)

        del st.session_state.edit_index

        st.success("Updated")

        st.rerun()


# -----------------------------------
# Summary
# -----------------------------------
if len(portfolio) > 0:

    st.subheader("Summary")

    profit = total_value - total_cost

    col1,col2,col3 = st.columns(3)

    col1.metric("Invested",f"${round(total_cost,2)}")
    col2.metric("Value",f"${round(total_value,2)}")
    col3.metric("Profit/Loss",f"${round(profit,2)}")
