import streamlit as st
import asyncio
import websockets
import json
from collections import deque
import numpy as np

st.set_page_config(page_title="Sinyal MA Real-time", layout="centered")
st.title("📡 Sinyal MA Trading Deriv (Real-time)")

symbol = st.selectbox("Pilih Pair", ["frxXAUUSD", "frxUSDJPY", "frxEURUSD", "R_100", "1HZ100V"])
ma_period = st.slider("Period MA", min_value=3, max_value=20, value=5)

# State
if "prices" not in st.session_state:
    st.session_state.prices = deque(maxlen=ma_period)
    st.session_state.prev_ma = None
    st.session_state.signal = "⏳ WAIT"
    st.session_state.prev_price = None

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

                # Hitung MA jika cukup data
                if len(st.session_state.prices) == ma_period:
                    ma_now = np.mean(st.session_state.prices)

                    prev_price = st.session_state.prev_price
                    prev_ma = st.session_state.prev_ma

                    if prev_price is not None and prev_ma is not None:
                        # BUY signal jika harga naik melewati MA
                        if prev_price < prev_ma and price > ma_now:
                            st.session_state.signal = "🔼 BUY"
                        # SELL signal jika harga turun melewati MA
                        elif prev_price > prev_ma and price < ma_now:
                            st.session_state.signal = "🔽 SELL"
                        else:
                            st.session_state.signal = "⏳ WAIT"

                    # Simpan state sebelumnya
                    st.session_state.prev_ma = ma_now
                    st.session_state.prev_price = price

                await asyncio.sleep(0.3)

async def main_loop():
    task = asyncio.create_task(fetch_price(symbol))
    while True:
        current_price = st.session_state.prices[-1] if st.session_state.prices else None
        ma_now = np.mean(st.session_state.prices) if len(st.session_state.prices) == ma_period else None

        st.metric("Harga", current_price)
        st.metric("MA", round(ma_now, 5) if ma_now else "Menunggu...")
        st.success(f"Sinyal: {st.session_state.signal}")

        await asyncio.sleep(0.5)

asyncio.run(main_loop())
