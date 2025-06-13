import streamlit as st
import asyncio
import websockets
import json
from collections import deque
import numpy as np

st.set_page_config(page_title="Sinyal MA Real-time", layout="centered")
st.title("📡 Sinyal MA Trading Deriv (Real-time Anti-Spam)")

symbol = st.selectbox("Pilih Pair", ["frxXAUUSD", "frxUSDJPY", "frxEURUSD", "R_100", "1HZ100V"])
ma_period = st.slider("Period MA", min_value=3, max_value=20, value=5)

# State Awal
if "prices" not in st.session_state:
    st.session_state.prices = deque(maxlen=ma_period)
    st.session_state.prev_price = None
    st.session_state.prev_ma = None
    st.session_state.last_signal = "WAIT"

async def fetch_price(symbol):
    url = "wss://ws.binaryws.com/websockets/v3?app_id=1089"
    async with websockets.connect(url) as ws:
        await ws.send(json.dumps({"ticks": symbol}))
        while True:
            response = await ws.recv()
            data = json.loads(response)

            if "tick" in data:
                price = float(data["tick"]["quote"])
                st.session_state.prices.append(price)

                # Hitung MA
                if len(st.session_state.prices) == ma_period:
                    ma_now = np.mean(st.session_state.prices)
                    prev_price = st.session_state.prev_price
                    prev_ma = st.session_state.prev_ma

                    signal = "WAIT"
                    if prev_price is not None and prev_ma is not None:
                        if prev_price < prev_ma and price > ma_now:
                            signal = "BUY"
                        elif prev_price > prev_ma and price < ma_now:
                            signal = "SELL"

                    # Tampilkan hanya jika sinyal BUY/SELL berubah
                    if signal in ["BUY", "SELL"] and signal != st.session_state.last_signal:
                        st.session_state.last_signal = signal
                        st.subheader(f"📈 Harga Sekarang: {price}")
                        st.success(f"💡 Sinyal: {signal}")
                    
                    # Simpan nilai sebelumnya
                    st.session_state.prev_ma = ma_now
                    st.session_state.prev_price = price

                await asyncio.sleep(0.3)

async def main_loop():
    await fetch_price(symbol)

asyncio.run(main_loop())
