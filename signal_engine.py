# signal_engine.py
→ Brain — fetches prices and generates signals
📄 signal_engine.py
COPY
# signal_engine.py
import os, requests, pandas as pd, ta

ALPHA_KEY = os.environ.get("ALPHA_KEY")

def get_price_data(pair):
    symbol = pair.replace("/", "")
    url = (
        "https://www.alphavantage.co/query"
        "?function=FX_INTRADAY"
        f"&from_symbol={symbol[:3]}"
        f"&to_symbol={symbol[3:]}"
        "&interval=15min"
        f"&apikey={ALPHA_KEY}"
    )
    data = requests.get(url).json()
    df   = pd.DataFrame(data["Time Series FX (15min)"]).T.astype(float)
    df.columns = ["open","high","low","close","volume"]
    return df.sort_index()

def get_signal(pair):
    df = get_price_data(pair)
    df["rsi"]         = ta.momentum.RSIIndicator(df["close"],14).rsi()
    m                 = ta.trend.MACD(df["close"])
    df["macd"]        = m.macd()
    df["macd_signal"] = m.macd_signal()
    df["ema_fast"]    = ta.trend.EMAIndicator(df["close"],9).ema_indicator()
    df["ema_slow"]    = ta.trend.EMAIndicator(df["close"],21).ema_indicator()
    last  = df.iloc[-1]
    price = last["close"]
    if (last["rsi"]<40 and last["macd"]>last["macd_signal"]
            and last["ema_fast"]>last["ema_slow"]):
        action, conf = "BUY", 80
    elif (last["rsi"]>60 and last["macd"]<last["macd_signal"]
            and last["ema_fast"]<last["ema_slow"]):
        action, conf = "SELL", 78
    else:
        action, conf = "HOLD", 0
    return {
        "pair": pair, "action": action, "confidence": conf,
        "entry": round(price,5),
        "sl": round(price-0.003,5) if action=="BUY" else round(price+0.003,5),
        "tp": round(price+0.006,5) if action=="BUY" else round(price-0.006,5),
        "rsi": round(last["rsi"],2),
        "macd": round(last["macd"],5),
    }
