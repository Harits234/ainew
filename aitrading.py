import streamlit as st
import yfinance as yf
import pandas as pd

# Konfigurasi halaman
st.set_page_config(page_title="Sinyal Trading Real-Time", layout="centered")
st.title("📈 Sinyal Trading Real-Time (MA Crossover)")

# Input simbol (XAUUSD diganti GLD sebagai representasi emas)
symbol = st.text_input("Masukkan Symbol (contoh: GLD, BTC-USD, EURUSD=X, AAPL)", value="GLD")

# Interval dan periode yang umum tersedia
interval = st.selectbox("Interval Data", ["1d", "1h", "15m", "5m"])
period = st.selectbox("Periode Data", ["5d", "7d", "1mo", "3mo"])

# Validasi symbol & interval (biar gak error)
supported_symbols = {
    "1d": ["GLD", "AAPL", "BTC-USD", "EURUSD=X", "JPY=X"],
    "1h": ["AAPL", "BTC-USD"],
    "15m": ["AAPL", "BTC-USD"],
    "5m": ["AAPL", "BTC-USD"]
}

if symbol not in supported_symbols.get(interval, []):
    st.warning(f"⚠️ Symbol '{symbol}' tidak tersedia untuk interval '{interval}' di Yahoo Finance. Silakan ganti symbol atau interval.")
    st.stop()

# Ambil data harga
@st.cache_data(ttl=60)
def get_data(symbol, period, interval):
    data = yf.download(tickers=symbol, period=period, interval=interval)
    data.dropna(inplace=True)
    return data

try:
    df = get_data(symbol, period, interval)

    if df.empty:
        st.error("❌ Data kosong. Coba ganti symbol atau cek koneksi.")
    else:
        df["MA5"] = df["Close"].rolling(window=5).mean()
        df["MA20"] = df["Close"].rolling(window=20).mean()

        # Grafik harga
        st.subheader("📊 Grafik Harga & Moving Average")
        chart_data = df[["Close", "MA5", "MA20"]].dropna()
        st.line_chart(chart_data)

        # Fungsi sinyal MA crossover
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

        # Output sinyal
        st.subheader("📣 Sinyal Saat Ini:")
        st.markdown(f"<h2 style='color: green;'>{signal}</h2>" if "BUY" in signal else
                    f"<h2 style='color: red;'>{signal}</h2>" if "SELL" in signal else
                    f"<h2>{signal}</h2>", unsafe_allow_html=True)

        # Data terakhir
        st.subheader("📅 Data Terakhir")
        st.write(df.tail(1))

except Exception as e:
    st.error(f"❌ Gagal mengambil data: {e}")
