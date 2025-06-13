import streamlit as st
import asyncio
import websockets
import json
import threading

st.set_page_config(page_title="Sinyal Deriv Realtime", layout="centered")
st.title("📡 Sinyal Trading Real-time dari Deriv")

symbol = st.selectbox("Pilih Pair", ["frxXAUUSD", "frxUSDJPY", "frxEURUSD", "R_100", "1HZ100V"])

st.markdown("### 💡 Sinyal")
signal_placeholder = st.empty()

st.markdown("### 💰 Harga Sekarang")
price_placeholder = st.empty()

# Global untuk menyimpan state harga terakhir
state = {"prev_price": None, "running": True}

async def deriv_listener(symbol):
    url = "wss://ws.binaryws.com/websockets/v3?app_id=1089"
    async with websockets.connect(url) as ws:
        await ws.send(json.dumps({"ticks": symbol}))
        while state["running"]:
            response = await ws.recv()
            data = json.loads(response)

            if "tick" in data:
                price = float(data["tick"]["quote"])
                prev = state["prev_price"]
                state["prev_price"] = price

                # Tentukan sinyal
                if prev is None:
                    signal = "⏳ WAIT"
                elif price > prev:
                    signal = "🔼 BUY"
                elif price < prev:
                    signal = "🔽 SELL"
                else:
                    signal = "⏳ WAIT"

                # Update UI
                price_placeholder.metric(label="Harga Saat Ini", value=price)
                signal_placeholder.markdown(f"<h2>{signal}</h2>", unsafe_allow_html=True)

def run_loop():
    asyncio.new_event_loop().run_until_complete(deriv_listener(symbol))

# Jalankan WebSocket listener di thread terpisah
thread = threading.Thread(target=run_loop)
thread.start()

# Tombol stop
if st.button("🛑 Hentikan"):
    state["running"] = False
    st.success("Sinyal dihentikan. Silakan refresh untuk memulai ulang.")
