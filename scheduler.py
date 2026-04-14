# scheduler.py
import os, schedule, time, requests
from signal_engine import get_signal
from broker import place_trade

TOKEN      = os.environ.get("TOKEN")
CHANNEL_ID = os.environ.get("CHANNEL_ID")
PAIRS      = ["EUR/USD","GBP/USD","USD/JPY"]

def send(msg):
    requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        data={"chat_id":CHANNEL_ID,"text":msg,"parse_mode":"Markdown"}
    )

def scan():
    for pair in PAIRS:
        s = get_signal(pair)
        if s["action"]=="HOLD":
            continue
        send(
            f"🚨 *{s['pair']} — {s['action']}*\n"
            f"Entry: {s['entry']}  SL: {s['sl']}  TP: {s['tp']}\n"
            f"Confidence: {s['confidence']}%"
        )
        if s["confidence"] >= 75:
            o = place_trade(s)
            send(
                f"✅ *Auto-Trade*\n"
                f"{pair} · {o['id']} · {o['price']} · {o['status']}"
            )

scan()
schedule.every(15).minutes.do(scan)
print("Scheduler running...")
while True:
    schedule.run_pending()
    time.sleep(1)
