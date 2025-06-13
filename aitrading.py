import streamlit as st
import asyncio
import websockets
import json

st.set_page_config(page_title="Sinyal Deriv Real-time", layout="centered")
st.title("📡 Sinyal Trading Deriv WebSocket")

symbol = st.selectbox("Pilih Pair", ["frxXAUUSD", "frxUSDJPY", "frxEURUSD", "R_100", "1HZ100V"])

# Inisialisasi session_state
if "price" not in st.session_state:
    st.session_state.price = None
    st.session_state.prev_price = None
    st.session_state.signal = "⏳ WAIT"

async def fetch_price(symbol):
    url = "wss://ws.binaryws.com/websockets/v3?app_id=1089"
    async with websockets.connect(url) as ws:
        await ws.send(json.dumps({"ticks": symbol}))
        while True:
            response = await ws.recv()
            data = json.loads(response)
            if "tick" in data:
                price = float(data["tick"]["quote"])
                prev = st.session_state.price
                st.session_state.prev_price = prev
                st.session_state.price = price

                # Update sinyal
                if prev is None:
                    st.session_state.signal = "⏳ WAIT"
                elif price > prev:
                    st.session_state.signal = "🔼 BUY"
                elif price < prev:
                    st.session_state.signal = "🔽 SELL"
                else:
                    st.session_state.signal = "⏳ WAIT"
                await asyncio.sleep(1)

async def main_loop():
    task = asyncio.create_task(fetch_price(symbol))
    while True:
        st.subheader(f"💰 Harga: {st.session_state.price}")
        st.success(f"Sinyal: {st.session_state.signal}")
        await asyncio.sleep(1)

# Jalankan loop utama
asyncio.run(main_loop())
