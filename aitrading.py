import streamlit as st
import asyncio
import websockets
import json
import numpy as np
import threading
import requests
from collections import deque

st.set_page_config(page_title="📡 Scalping Signal - Telegram", layout="centered")
st.title("📈 AI TRADING The Pip Mafia")

# State & memory
if "telegram_ids" not in st.session_state:
    st.session_state.telegram_ids = set()
if "running" not in st.session_state:
    st.session_state.running = False

# UI: input telegram id
telegram_input = st.text_input("Masukkan ID Telegram Anda (maks 5 pengguna)")
pair = st.selectbox("Pilih Pair", ["frxXAUUSD", "frxUSDJPY", "frxEURUSD", "R_100"])

if st.button("Daftar & Jalankan Bot"):
    if len(st.session_state.telegram_ids) >= 5:
        st.error("⚠️ Maksimal 5 ID Telegram")
    else:
        st.session_state.telegram_ids.add(telegram_input)
        st.session_state.running = True
        st.success(f"✅ ID {telegram_input} didaftarkan!")

# Constants
MA_FAST = 50
MA_SLOW = 200
prices = deque(maxlen=MA_SLOW)
last_signal = None

TELEGRAM_BOT_TOKEN = "8125493408:AAGnuSkf_BwscznH9B_gjzSTNOrVgSd0jos"

def send_telegram_signal(signal, price, pair):
    for user_id in st.session_state.telegram_ids:
        message = f"\n📉 *Sinyal Scalping - {pair}*\n🔔 *Sinyal:* {signal}\n💰 *Harga:* {price:.2f}\n📊 *Strategi:* MA50/200 Cross"
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {"chat_id": user_id, "text": message, "parse_mode": "Markdown"}
        requests.post(url, data=payload)

# WebSocket Deriv
async def deriv_ws():
    global last_signal
    uri = "wss://ws.binaryws.com/websockets/v3?app_id=1089"
    async with websockets.connect(uri) as ws:
        await ws.send(json.dumps({"ticks": pair}))
        while True:
            msg = json.loads(await ws.recv())
            if "tick" in msg:
                price = float(msg["tick"]["quote"])
                prices.append(price)

                if len(prices) >= MA_SLOW:
                    ma50 = np.mean(list(prices)[-MA_FAST:])
                    ma200 = np.mean(list(prices))

                    if ma50 > ma200 and last_signal != "BUY":
                        send_telegram_signal("BUY", price, pair)
                        last_signal = "BUY"
                    elif ma50 < ma200 and last_signal != "SELL":
                        send_telegram_signal("SELL", price, pair)
                        last_signal = "SELL"
            await asyncio.sleep(0.5)

def run_ws():
    asyncio.run(deriv_ws())

if st.session_state.running:
    threading.Thread(target=run_ws, daemon=True).start()
    st.success("🚀 Bot berjalan realtime dan akan mengirim sinyal jika MA50 cross MA200")
