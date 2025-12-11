import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf

ticker = "TSLA"
df = yf.download(ticker, start="2025-01-01", end="2025-12-09", auto_adjust=False)   

data = pd.DataFrame(index=df.index)
data["Price"] = df["Close"]

window = 20
data["MA20"] = data["Price"].rolling(window).mean()
data["STD20"] = data["Price"].rolling(window).std()
data["UpperBand"] = data["MA20"] + 2 * data["STD20"]
data["LowerBand"] = data["MA20"] - 2 * data["STD20"]

data["Signal"] = 0
data.loc[data["Price"] < data["LowerBand"], "Signal"] = 1
data.loc[data["Price"] > data["UpperBand"], "Signal"] = -1
data["Position"] = data["Signal"].replace(0, np.nan).ffill().fillna(0)

data["Price_Return"] = data["Price"].pct_change()
data["Strategy_Return"] = data["Position"].shift(1) * data["Price_Return"]
data["Equity"] = (1 + data["Strategy_Return"]).cumprod()

plt.figure(figsize=(14,6))
plt.plot(data.index, data["Price"], label="Price")
plt.plot(data.index, data["MA20"], label="MA20", linestyle="--")
plt.plot(data.index, data["UpperBand"], label="Upper Band", linestyle="--")
plt.plot(data.index, data["LowerBand"], label="Lower Band", linestyle="--")

plt.scatter(data.index[data["Signal"] == 1], data["Price"][data["Signal"] == 1],
            marker="^", color="green", label="Buy", s=80)
plt.scatter(data.index[data["Signal"] == -1], data["Price"][data["Signal"] == -1],
            marker="v", color="red", label="Sell", s=80)

plt.title("Mean Reversion Strategy using Bollinger Bands on TSLA")
plt.legend()
plt.show()

plt.figure(figsize=(12,4))
plt.plot(data.index, data["Equity"])
plt.title("Equity Curve — TSLA strategy")
plt.xlabel("Date")
plt.ylabel("Portfolio Value (relative)")
plt.show()
