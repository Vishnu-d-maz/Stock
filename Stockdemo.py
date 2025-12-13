# ==============================
# 1. IMPORTS
# ==============================
from kiteconnect import KiteConnect
import pandas as pd
import numpy as np
import time
import datetime as dt

print("🔥 FILE STARTED EXECUTING 🔥")


# ==============================
# 2. KITE API SETUP
# ==============================
API_KEY = "0x1niqzaa6tvxuid"
ACCESS_TOKEN = "JyAmP7JfkNlMJgKSLDhlVCUA2FLHC05P"

kite = KiteConnect(api_key=API_KEY)
kite.set_access_token(ACCESS_TOKEN)

# ==============================
# 3. GLOBAL CONFIG
# ==============================
SYMBOL = "NIFTY"
INSTRUMENT_TOKEN = 256265
LOT_SIZE = 25
INTERVAL = "5minute"
TARGET_POINTS = 2
STOPLOSS_POINTS = 2

# ==============================
# 4. DATA FETCHING
# ==============================
def get_5min_data(token):
    to_date = dt.datetime.now()
    from_date = to_date - dt.timedelta(days=5)

    data = kite.historical_data(
        token,
        from_date,
        to_date,
        interval=INTERVAL,
        oi=True
    )
    return pd.DataFrame(data)

# ==============================
# 5. INDICATORS – BOLLINGER
# ==============================
def add_bollinger_bands(df, period=20, std=2):
    df['SMA'] = df['close'].rolling(period).mean()
    df['STD'] = df['close'].rolling(period).std()
    df['Upper'] = df['SMA'] + std * df['STD']
    df['Lower'] = df['SMA'] - std * df['STD']
    return df

# ==============================
# 6. MEAN REVERSION SIGNAL
# ==============================
def get_signal(df):
    last = df.iloc[-1]
    if last['close'] <= last['Lower']:
        return "BUY"
    elif last['close'] >= last['Upper']:
        return "SELL"
    return "HOLD"

# ==============================
# 7. OPTION SELECTION
# ==============================
def get_nearest_expiry(symbol):
    instruments = pd.DataFrame(kite.instruments("NFO"))
    return sorted(
        instruments[instruments['name'] == symbol]['expiry'].unique()
    )[0]

def select_option(symbol, signal, spot_price):
    instruments = pd.DataFrame(kite.instruments("NFO"))
    expiry = get_nearest_expiry(symbol)

    df = instruments[
        (instruments['name'] == symbol) &
        (instruments['expiry'] == expiry)
    ]

    df['distance'] = abs(df['strike'] - spot_price)
    df = df[df['distance'] <= 200]

    if signal == "BUY":
        option = df[df['instrument_type'] == "CE"].sort_values('distance').iloc[0]
    else:
        option = df[df['instrument_type'] == "PE"].sort_values('distance').iloc[0]

    return option['tradingsymbol']

# ==============================
# 8. ORDER & TRADE MANAGEMENT
# ==============================
def place_buy_order(symbol):
    return kite.place_order(
        variety=kite.VARIETY_REGULAR,
        exchange=kite.EXCHANGE_NFO,
        tradingsymbol=symbol,
        transaction_type=kite.TRANSACTION_TYPE_BUY,
        quantity=LOT_SIZE,
        order_type=kite.ORDER_TYPE_MARKET,
        product=kite.PRODUCT_MIS
    )

def exit_trade(symbol):
    kite.place_order(
        variety=kite.VARIETY_REGULAR,
        exchange=kite.EXCHANGE_NFO,
        tradingsymbol=symbol,
        transaction_type=kite.TRANSACTION_TYPE_SELL,
        quantity=LOT_SIZE,
        order_type=kite.ORDER_TYPE_MARKET,
        product=kite.PRODUCT_MIS
    )

def manage_trade(symbol, buy_price):
    target = buy_price + TARGET_POINTS
    stoploss = buy_price - STOPLOSS_POINTS

    while True:
        ltp = kite.ltp(f"NFO:{symbol}")[f"NFO:{symbol}"]['last_price']

        if ltp >= target or ltp <= stoploss:
            exit_trade(symbol)
            break

        time.sleep(2)

# ==============================
# 9. MAIN LOOP (5 MIN)
# ==============================
def main():
    while True:
        try:
            df = get_5min_data(INSTRUMENT_TOKEN)
            df = add_bollinger_bands(df)

            signal = get_signal(df)
            spot_price = df.iloc[-1]['close']

            if signal in ["BUY", "SELL"]:
                option_symbol = select_option(SYMBOL, signal, spot_price)
                place_buy_order(option_symbol)

                buy_price = kite.ltp(
                    f"NFO:{option_symbol}"
                )[f"NFO:{option_symbol}"]['last_price']

                manage_trade(option_symbol, buy_price)

            time.sleep(300)

        except Exception as e:
            print("Error:", e)
            time.sleep(5)

# ==============================
# 10. ENTRY POINT
# ==============================
if __name__ == "__main__":
    main()
