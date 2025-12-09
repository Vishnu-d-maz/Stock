import yfinance as yf
import pandas as pd
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
import requests
import os

# ======================================================
#  LOAD SECRETS FROM ENVIRONMENT VARIABLES (SAFEST WAY)
# ======================================================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_APP_PASSWORD")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")

# ======================================================
# SEND TELEGRAM MESSAGE
# ======================================================
def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    params = {"chat_id": CHAT_ID, "text": msg}
    requests.get(url, params=params)

# ======================================================
# SEND EMAIL
# ======================================================
def send_email(subject, body):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = EMAIL_SENDER
    msg["To"] = EMAIL_RECEIVER

    server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    server.login(EMAIL_SENDER, EMAIL_PASSWORD)
    server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())
    server.quit()

# ======================================================
# STOCK SIGNAL LOGIC
# ======================================================
def check_signal(stock):
    try:
        df = yf.download(stock, period="6mo", auto_adjust=True)
        df["SMA20"] = df["Close"].rolling(20).mean()
        df["SMA50"] = df["Close"].rolling(50).mean()

        last = df.iloc[-1]

        if last["SMA20"] > last["SMA50"]:
            return f"📈 BUY Signal for {stock}\nPrice: {last['Close']}"
        elif last["SMA20"] < last["SMA50"]:
            return f"📉 SELL Signal for {stock}\nPrice: {last['Close']}"
        else:
            return None
    except Exception as e:
        return f"Error fetching {stock}: {str(e)}"

# ======================================================
# MAIN LOOP
# ======================================================
stocks = ["INFY.NS", "TCS.NS", "RELIANCE.NS", "HDFCBANK.NS"]

all_messages = []

for s in stocks:
    signal = check_signal(s)
    if signal:
        all_messages.append(signal)

# SEND ALL SIGNALS TO TELEGRAM + EMAIL
if all_messages:
    message_text = "\n\n".join(all_messages)
    send_telegram(message_text)
    send_email("Stock Signals Update", message_text)
else:
    send_telegram("No signals today.")
