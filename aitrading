# sinyal_trading_app.py

import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# Judul halaman
st.set_page_config(page_title="Sinyal Trading Real-Time", layout="centered")
st.title("📈 Sinyal Trading Real-Time (MA Crossover)")

# Input symbol
symbol = st.text_input("Masukkan Symbol (contoh: XAUUSD=X untuk Gold, EURUSD=X, BTC-USD, AAPL)", value="XAUUSD=X")

# Rentang waktu
interval = st.selectbox("Interval Data", ["1m", "5m", "15m", "1h", "1d"])
period = st.selectbox("Periode Data", ["1d", "5d", "7d", "1mo", "3mo"])

# Ambil data dari Yahoo Finance
@st.cache_data(ttl=60)  # cache selama 60 detik
def get_data(symbol, period, interval):
    data = yf.download(tickers=symbol, period=period, interval=interval)
    data.dropna(inplace=True)
    return data

try:
    df = get_data(symbol, period, interval)
    df["MA5"] = df["Close"].rolling(window=5).mean()
    df["MA20"] = df["Close"].rolling(window=20).mean()

    # Tampilkan chart harga
    st.subheader("Grafik Harga & Moving Average")
    st.line_chart(df[["Close", "MA5", "MA20"]])

    # Deteksi sinyal terakhir
    def get_signal(data):
        if len(data) < 21:
            return "Data tidak cukup"
        if data["MA5"].iloc[-2] < data["MA20"].iloc[-2] and data["MA5"].iloc[-1] > data["MA20"].iloc[-1]:
            return "🔼 BUY"
        elif data["MA5"].iloc[-2] > data["MA20"].iloc[-2] and data["MA5"].iloc[-1] < data["MA20"].iloc[-1]:
            return "🔽 SELL"
        else:
            return "⏳ WAIT"

    signal = get_signal(df)
    st.subheader("📣 Sinyal Saat Ini:")
    st.markdown(f"<h2 style='color: green;'>{signal}</h2>" if "BUY" in signal else
                f"<h2 style='color: red;'>{signal}</h2>" if "SELL" in signal else
                f"<h2>{signal}</h2>", unsafe_allow_html=True)

    # Tampilkan data terakhir
    st.subheader("Data Terakhir")
    st.write(df.tail(1))

except Exception as e:
    st.error(f"❌ Gagal mengambil data: {e}")
