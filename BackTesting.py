import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt

data = yf.download("TSLA", start="2025-01-01", end="2025-12-10", auto_adjust=True)

if isinstance(data.columns, pd.MultiIndex):
    data.columns = ['_'.join([str(c) for c in col if c!='']).strip() for col in data.columns]

close_cols = [c for c in data.columns if "Close" in c]
close_col = close_cols[0]
data.rename(columns={close_col: "Close"}, inplace=True)

data['MA50'] = data['Close'].rolling(50).mean()
data = data.dropna()

data['Signal'] = (data['Close'] > data['MA50']).astype(int)
data['Position'] = data['Signal'].diff().fillna(0)

buy_signals = data[data['Position'] == 1]
sell_signals = data[data['Position'] == -1]

plt.figure(figsize=(14, 7))

plt.plot(data['Close'], label='Close Price')
plt.plot(data['MA50'], label='MA50', linewidth=1.5)

plt.scatter(
    buy_signals.index,
    buy_signals['Close'],
    marker='^', color='green', s=100, label='Buy'
)

plt.scatter(
    sell_signals.index,
    sell_signals['Close'],
    marker='v', color='red', s=100, label='Sell'
)

plt.title("TSLA Backtest: MA50 Strategy (Buy/Sell Signals)")
plt.xlabel("Date")
plt.ylabel("Price")
plt.legend()
plt.grid(True)
plt.show()
