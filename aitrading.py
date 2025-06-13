import streamlit as st
import asyncio
import websockets
import json
import numpy as np
from collections import deque

st.set_page_config(page_title="Sinyal Realtime MA", layout="centered")
st.title("📡 Realtime Trading Signal - MA Strategy")

# UI: Pilihan pair & periode MA
symbol = st.selectbox("Pilih Pair Deriv", ["frxXAUUSD", "frxUSDJPY", "frxEURUSD", "R_100"], index=0)
ma_period = st.slider("Period MA", 3, 20, 5)

# Komponen display
price_placeholder = st.empty()
ma_placeholder = st.empty()
signal_placeholder = st.empty()

# State penyimpanan
prices = deque(maxlen=ma_period)
last_signal = "WAIT"

# Fungsi WebSocket Deriv
async def get_ticks(symbol):
    global last_signal
    uri = "wss://ws.binaryws.com/websockets/v3?app_id=1089"
    async with websockets.connect(uri) as ws:
        await ws.send(json.dumps({"ticks": symbol}))
        prev_price, prev_ma = None, None

        while True:
            response = json.loads(await ws.recv())
            if "tick" in response:
                price = float(response["tick"]["quote"])
                prices.append(price)

                price_placeholder.metric("Harga", f"{price:.2f}")

                if len(prices) == ma_period:
                    ma = np.mean(prices)
                    ma_placeholder.markdown(f"**MA({ma_period})**: {ma:.2f}")

                    # Cross logic
                    if prev_price is not None and prev_ma is not None:
                        signal = "WAIT"
                        if prev_price < prev_ma and price > ma:
                            signal = "BUY"
                        elif prev_price > prev_ma and price < ma:
                            signal = "SELL"

                        # Tampilkan sinyal hanya saat berubah
                        if signal != "WAIT" and signal != last_signal:
                            signal_placeholder.success(f"💡 Sinyal: {signal}")
                            last_signal = signal

                    prev_price = price
                    prev_ma = ma
            await asyncio.sleep(0.5)

# Jalankan event loop
asyncio.run(get_ticks(symbol))
