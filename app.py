import streamlit as st
import pandas as pd
import sqlite3
import os

st.set_page_config(page_title="Cross Market Analysis", layout="wide")

# ---------- DATABASE CONNECTION ----------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "cross_market.db")
conn = sqlite3.connect(db_path, check_same_thread=False)

# ---------- SIDEBAR ----------
page = st.sidebar.selectbox(
    "Select Page",
    ["Market Overview", "SQL Query Runner", "Top Crypto Analysis"]
)

# ---------- PAGE 1 ----------
if page == "Market Overview":
    st.title("📊 Cross-Market Overview")

    start_date = st.date_input(
        "Start Date", pd.to_datetime("2025-01-01")
    ).strftime("%Y-%m-%d")

    end_date = st.date_input(
        "End Date", pd.to_datetime("2025-12-31")
    ).strftime("%Y-%m-%d")

    query = f"""
    SELECT c.date,
           c.price_usd AS bitcoin_price,
           o.price_usd AS oil_price,
           s.close AS sp500_close
    FROM crypto_prices c
    JOIN oil_prices o ON c.date = o.date
    JOIN stock_prices s ON c.date = s.date
    WHERE c.coin_id='bitcoin'
      AND s.ticker='^GSPC'
      AND c.date BETWEEN '{start_date}' AND '{end_date}'
    """

    try:
        df = pd.read_sql(query, conn)
    except Exception as e:
        st.error(f"Database error: {e}")
        st.stop()

    if df.empty:
        st.warning("No data found for selected date range.")
        st.stop()

    col1, col2, col3 = st.columns(3)
    col1.metric("Bitcoin Avg Price", round(df['bitcoin_price'].mean(), 2))
    col2.metric("Oil Avg Price", round(df['oil_price'].mean(), 2))
    col3.metric("S&P 500 Avg Close", round(df['sp500_close'].mean(), 2))

    st.line_chart(df.set_index("date"))
    st.dataframe(df)

# ---------- PAGE 2 ----------
elif page == "SQL Query Runner":
    st.title("🧮 Run SQL Queries")

    queries = {
        "Top 3 Cryptos": "SELECT name, market_cap FROM cryptocurrencies ORDER BY market_cap DESC LIMIT 3;",
        "Oil Avg Price 2025": "SELECT AVG(price_usd) FROM oil_prices;",
        "NASDAQ Highest Close": "SELECT MAX(close) FROM stock_prices WHERE ticker='^IXIC';"
    }

    selected_query = st.selectbox("Choose Query", list(queries.keys()))

    if st.button("Run Query"):
        result = pd.read_sql(queries[selected_query], conn)
        st.dataframe(result)

# ---------- PAGE 3 ----------
elif page == "Top Crypto Analysis":
    st.title("🪙 Crypto Price Trend")

    coins = pd.read_sql(
        "SELECT id FROM cryptocurrencies ORDER BY market_cap_rank LIMIT 3;",
        conn
    )

    selected_coin = st.selectbox("Select Coin", coins['id'])

    start_date = st.date_input("Start Date").strftime("%Y-%m-%d")
    end_date = st.date_input("End Date").strftime("%Y-%m-%d")

    query = f"""
    SELECT date, price_usd
    FROM crypto_prices
    WHERE coin_id='{selected_coin}'
      AND date BETWEEN '{start_date}' AND '{end_date}'
    """

    df = pd.read_sql(query, conn)
    st.line_chart(df.set_index("date"))
    st.dataframe(df)
