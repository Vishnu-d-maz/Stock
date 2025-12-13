from kiteconnect import KiteConnect

api_key = "0x1niqzaa6tvxuid"
api_secret = "tl09n73dz4xt2k0epbe1gi72qd6hdyj4"
request_token = "jOZDkut4CpF3UH7n9IPlbAR63ZzdnKXI"

kite = KiteConnect(api_key=api_key)

data = kite.generate_session(request_token, api_secret=api_secret)
access_token = data["access_token"]

kite.set_access_token(access_token)

print(access_token)
profile = kite.profile()
print(profile)

