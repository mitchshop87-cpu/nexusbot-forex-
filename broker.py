# broker.py
COPY
# broker.py
import os, requests

OANDA_KEY  = os.environ.get("OANDA_KEY")
ACCOUNT_ID = os.environ.get("ACCOUNT_ID")
BASE_URL   = "https://api-fxtrade.oanda.com/v3"
HEADERS    = {
    "Authorization": f"Bearer {OANDA_KEY}",
    "Content-Type":  "application/json"
}

def get_balance():
    res = requests.get(
        f"{BASE_URL}/accounts/{ACCOUNT_ID}/summary",
        headers=HEADERS
    ).json()
    acc = res["account"]
    return {
        "balance":       acc["balance"],
        "currency":      acc["currency"],
        "unrealized_pl": acc["unrealizedPL"]
    }

def place_trade(signal):
    pair  = signal["pair"].replace("/","_")
    units = 1000 if signal["action"]=="BUY" else -1000
    order = {"order":{
        "type":"MARKET","instrument":pair,
        "units":str(units),"timeInForce":"FOK",
        "positionFill":"DEFAULT",
        "stopLossOnFill":  {"price":str(signal["sl"])},
        "takeProfitOnFill":{"price":str(signal["tp"])},
    }}
    res  = requests.post(
        f"{BASE_URL}/accounts/{ACCOUNT_ID}/orders",
        headers=HEADERS, json=order
    ).json()
    fill = res.get("orderFillTransaction",{})
    return {
        "id":    fill.get("id","N/A"),
        "price": fill.get("price","N/A"),
        "status":"FILLED" if fill else "FAILED"
    }
