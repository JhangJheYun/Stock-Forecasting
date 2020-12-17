from config import Session
from schema import Stock, History
import pandas as pd
import os

def K_Means():

    #stocks = Session.query(Stock).all()

    for stock in [1101]:
        trans = Session.query(History).filter(stock == History.id).all()
        if len(trans) == 0:
            print(stock.id, 'not exist in DB.')
            continue
        else:
            # for row in range(1, len(trans)):
            #     print((trans[row].high-trans[row].low) / row
            #     #print(stock.id, high, low)
            df = pd.DataFrame([(i.id, i.date.strftime('%Y-%m-%d'), i.high, i.low, i.close, i.volume) for i in trans], 
                              columns=['id', 'date', 'high', 'low', 'close', 'volume'])
            df = df.set_index('date')
            print(df.iloc[:15])
            df = df.sort_values(['date'])
            print(df.iloc[:15])
            #for index, data in df.iterrows():
            df['amplitude'] = (df['high']-df['low']) / df['close'].shift(1) * 100
            amplitude = [0 for _ in range(11)]
            for i in df['amplitude'][1:]:
                amplitude[int(i)] += 1
            print(amplitude)
            print(sum(df['amplitude'][1:])/(len(df)-1))
            print(sum(df['volume'][1:])/(len(df)-1))
            print(sum(df['close'][1:])/(len(df)-1))
            print(max(df['high']))
            print(max(df['low']))
            print(max(df['close']))
            print(min(df['high']))
            print(min(df['low']))
            print(min(df['close']))


K_Means()