# ============================================
# MEAN REVERSION USING BOLLINGER BANDS
# REAL BUY / SELL SIGNALS | 1-MIN
# ============================================

print("🔥 FILE STARTED", flush=True)

from kiteconnect import KiteConnect
import pandas as pd
import datetime as dt
import time

# ============================================
# KITE API SETUP
# ============================================
API_KEY = "0x1niqzaa6tvxuid"
ACCESS_TOKEN = "AKCw2vhD0Sgl5ETLWKJt6VUl3GVjT6pS"

kite = KiteConnect(api_key=API_KEY)
kite.set_access_token(ACCESS_TOKEN)

print("✅ Kite connected", flush=True)

# ============================================
# CONFIGURATION (CHANGE HERE)
# ============================================
SYMBOL = "RELIANCE"      # CHANGE
INSTRUMENT_TOKEN = 738561  # CHANGE
LOT_SIZE = 250           # CHANGE

INTERVAL = "minute"
PAPER_TRADING = True

# ============================================
# LOAD INSTRUMENTS
# ============================================
print("⏳ Loading instruments...", flush=True)
INSTRUMENTS = pd.DataFrame(kite.instruments("NFO"))
print("✅ Instruments loaded", flush=True)

# ============================================
# FUNCTIONS
# ============================================

def get_1min_data(token):
    to_date = dt.datetime.now()
    from_date = to_date - dt.timedelta(days=2)

    data = kite.historical_data(
        token,
        from_date,
        to_date,
        interval=INTERVAL,
        oi=True
    )
    return pd.DataFrame(data)


def add_bollinger(df, period=5):   # 5 for fast demo
    df["SMA"] = df["close"].rolling(period).mean()
    df["STD"] = df["close"].rolling(period).std()
    df["UPPER"] = df["SMA"] + 2 * df["STD"]
    df["LOWER"] = df["SMA"] - 2 * df["STD"]
    return df


def get_signal(df):
    last = df.iloc[-1]

    if last["close"] <= last["LOWER"]:
        return "BUY"
    elif last["close"] >= last["UPPER"]:
        return "SELL"
    return "HOLD"


def get_nearest_expiry(symbol):
    df = INSTRUMENTS[INSTRUMENTS["name"] == symbol]
    return sorted(df["expiry"].unique())[0]


def select_option(symbol, signal, spot_price):
    expiry = get_nearest_expiry(symbol)

    df = INSTRUMENTS[
        (INSTRUMENTS["name"] == symbol) &
        (INSTRUMENTS["expiry"] == expiry)
    ].copy()

    df["distance"] = abs(df["strike"] - spot_price)
    df = df[df["distance"] <= 200]

    if df.empty:
        return None

    if signal == "BUY":
        opt = df[df["instrument_type"] == "CE"]
    else:
        opt = df[df["instrument_type"] == "PE"]

    return opt.sort_values("distance").iloc[0]["tradingsymbol"]


def demo_trade(option, signal):
    print(f"🧪 PAPER {signal} → {option}", flush=True)
    print("🎯 Target: +2 | 🛑 SL: -2\n", flush=True)

# ============================================
# MAIN LOOP
# ============================================
def main():
    print("🚀 Strategy Started (REAL BOLLINGER)", flush=True)

    while True:
        df = get_1min_data(INSTRUMENT_TOKEN)

        if df is None or len(df) < 5:
            print("⏳ Waiting for sufficient candles...", flush=True)
            time.sleep(10)
            continue

        df = add_bollinger(df)
        signal = get_signal(df)
        spot_price = df.iloc[-1]["close"]

        print(f"📊 Signal: {signal} | Spot: {spot_price}", flush=True)

        if signal in ["BUY", "SELL"]:
            option = select_option(SYMBOL, signal, spot_price)
            if option:
                demo_trade(option, signal)

        print("⏳ Waiting for next candle...\n", flush=True)
        time.sleep(60)


if __name__ == "__main__":
    main()
