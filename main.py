from binance import Client
import numpy as np
from datetime import datetime, timedelta, date
import time
import numpy as np
from model import LM

class Cache:
    def __init__(self, sum, alpha):
        self.crypto = 0
        self.dollars = sum
        self.coms = alpha

    def buy(self, q):
        p = client.get_avg_price(symbol=PAIR)
        s = p * q
        assert s >= 10 # BTC-USD
        self.dollars -= '%.2f'%(s * (1 + self.coms))
        self.crypto ='%.6f'%(q) 

    def sell(self, q):
        assert self.crypto >= q
        p = client.get_avg_price(symbol=PAIR)
        s = p * q
        assert s >= 10
        self.crypto -= '%.6f'%(q)
        self.dollars = '%.2f'%(s)

def get_data():
    '''
    [
    [
        1499040000000,      // Open time
        "0.01634790",       // Open
        "0.80000000",       // High
        "0.01575800",       // Low
        "0.01577100",       // Close
        "148976.11427815",  // Volume
        1499644799999,      // Close time
        "2434.19055334",    // Quote asset volume
        308,                // Number of trades
        "1756.87402397",    // Taker buy base asset volume
        "28.46694368",      // Taker buy quote asset volume
        "17928899.62484339" // Ignore.
    ]
    ]
    '''
    df = client.get_klines(
        symbol='BTCUSDT', interval=INTERVAL, limit=1000)
    df = np.array(df)
    times = [datetime(1970, 1, 1) + timedelta(milliseconds=int(ms))
            for ms in df[:, 6]]
    prices = df[:, 4]

    assert times[len(times)-1].day == date.today().day
    return np.array(times), np.array(prices).astype(np.float64)

def predict():
    _, ts = get_data()
    p1 = ts[-3]
    p2 = ts[-2]
    p3 = ts[-1]
    return p3 + p3 * ((1 - p2 / p3)/2 + (1- p1/p3))/2


def get_price():
    d = client.get_avg_price(symbol=PAIR)
    return float(d['price'])

def open_position():
    global BULL
    predPrice = predict()
    price = get_price()
    # long position
    if predPrice >= price:
        BULL = True
        print(f"up {predPrice} {price}")
    else:
        BULL = False 
        print(f"down {predPrice} {price}")
    time.sleep(SLEEP_DURATION)
    return price
        

def close_position(lastPrice):
    global score
    price = get_price()
    if price >= lastPrice and BULL or price < lastPrice and not BULL:
        score += 1
        print(f"+ {price}")

    if price < lastPrice and BULL or price >= lastPrice and not BULL:
        print(f"- {price}")

api_key = ''
api_secret = ''
CURRENCY = 'BTC'
PAIR = 'BTCUSDT'
INTERVAL = Client.KLINE_INTERVAL_5MINUTE
SUM = 11 # dollars
SLEEP_DURATION = 5 * 60 # secs

BULL = True
profit = 0.003
coms = 0.001

client = Client(api_key, api_secret)
score = 0

if __name__ == '__main__':
    t = 0
    while True:
        lastPrice = open_position()
        close_position(lastPrice)
        t += 1
        print(f"score {score} / {t}")
