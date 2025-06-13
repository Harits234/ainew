import streamlit as st
import asyncio
import websockets
import json
import numpy as np
from collections import deque
import threading

st.set_page_config(page_title="📡 Sinyal Trading MA", layout="centered")
st.title("📈 Realtime Sinyal Trading - Moving Average")

# Input UI
symbol = st.selectbox("Pilih Pair", ["frxXAUUSD", "frxUSDJPY", "frxEURUSD", "R_100"], index=0)
ma_period = st.slider("MA Period", 3, 20, 5)

# State
prices = deque(maxlen=ma_period)
last_signal = st.session_state.get("last_signal", "NONE")
prev_price = None
prev_ma = None

# Placeholder UI
price_ph = st.empty()
ma_ph = st.empty()
signal_ph = st.empty()

# Realtime WebSocket Handler
def start_deriv_ws():
    async def deriv_stream():
        global prev_price, prev_ma, last_signal
        uri = "wss://ws.binaryws.com/websockets/v3?app_id=1089"
        async with websockets.connect(uri) as ws:
            await ws.send(json.dumps({"ticks": symbol}))
            while True:
                msg = json.loads(await ws.recv())
                if "tick" in msg:
                    price = float(msg["tick"]["quote"])
                    prices.append(price)
                    price_ph.metric("Harga", f"{price:.2f}")

                    if len(prices) == ma_period:
                        ma_val = np.mean(prices)
                        ma_ph.markdown(f"**MA({ma_period})** = `{ma_val:.2f}`")

                        signal = "NONE"
                        if prev_price and prev_ma:
                            if prev_price < prev_ma and price > ma_val:
                                signal = "BUY"
                            elif prev_price > prev_ma and price < ma_val:
                                signal = "SELL"

                        if signal != "NONE" and signal != last_signal:
                            signal_ph.success(f'<div id="signal">💡 <b>Sinyal:</b> {signal}</div>', unsafe_allow_html=True)
                            st.markdown(
                                """
                                <script>
                                    document.getElementById("signal").scrollIntoView({ behavior: 'smooth' });
                                </script>
                                """,
                                unsafe_allow_html=True
                            )
                            st.session_state["last_signal"] = signal
                            last_signal = signal

                        prev_price = price
                        prev_ma = ma_val
                await asyncio.sleep(0.5)

    asyncio.run(deriv_stream())

# Jalankan WebSocket di thread agar tidak memblok UI Streamlit
thread = threading.Thread(target=start_deriv_ws)
thread.start()
