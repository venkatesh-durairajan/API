import streamlit as st
import pandas as pd
import os

FILE_NAME = "stocks.csv"

# Load stocks
def load_stocks():
    if os.path.exists(FILE_NAME):
        return pd.read_csv(FILE_NAME)
    else:
        return pd.DataFrame(columns=["Ticker", "Shares", "Price"])

# Save stocks
def save_stocks(df):
    df.to_csv(FILE_NAME, index=False)

st.title("📈 My Stock Portfolio")

df = load_stocks()

st.subheader("Add Stock")

with st.form("add_stock_form"):
    ticker = st.text_input("Ticker")
    shares = st.number_input("Shares", min_value=0.0)
    price = st.number_input("Price", min_value=0.0)
    submit = st.form_submit_button("Add Stock")

    if submit:
        new_row = pd.DataFrame({
            "Ticker": [ticker],
            "Shares": [shares],
            "Price": [price]
        })
        df = pd.concat([df, new_row], ignore_index=True)
        save_stocks(df)
        st.success("Stock added successfully!")
        st.experimental_rerun()

st.divider()

st.subheader("Edit / Delete Stocks")

if len(df) > 0:

    edited_df = st.data_editor(
        df,
        num_rows="dynamic",
        use_container_width=True
    )

    col1, col2 = st.columns(2)

    with col1:
        if st.button("💾 Save Changes"):
            save_stocks(edited_df)
            st.success("Changes saved!")

    with col2:
        if st.button("🗑 Delete Selected Rows"):
            selected_rows = st.multiselect(
                "Select rows to delete",
                options=df.index,
                format_func=lambda x: df.loc[x, "Ticker"]
            )
            df = df.drop(selected_rows)
            save_stocks(df)
            st.experimental_rerun()

else:
    st.info("No stocks added yet.")

st.divider()

st.subheader("Portfolio Summary")

if len(df) > 0:
    df["Value"] = df["Shares"] * df["Price"]
    total = df["Value"].sum()

    st.dataframe(df)

    st.metric("Total Portfolio Value", f"${total:,.2f}")
