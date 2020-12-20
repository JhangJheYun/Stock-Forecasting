from config import Session
from schema import Stock, History, Analysis
import pandas as pd
import numpy as np
import os

def K_Means():

    stocks = Session.query(Stock).all()
    for stock in stocks:
        trans = Session.query(History).filter(stock.id == History.id).all()
        if len(trans) == 0:
            print(stock.id, 'not exist in DB.')
            continue
        else:
            df = pd.DataFrame([(i.id, i.date.strftime('%Y-%m-%d'), i.high, i.low, i.close, i.volume) for i in trans], 
                              columns=['id', 'date', 'high', 'low', 'close', 'volume'])
            df = df.set_index('date')
            df = df.sort_values(['date'])

            df['amplitude'] = (df['high']-df['low']) / df['close'].shift(1) * 100
            amplitude = '%.2f' % (sum(df['amplitude'][-121:-1])/120)
            ma_5 = '%.2f' % (sum(df['close'][-6:-1])/5)
            ma_20 = '%.2f' % (sum(df['close'][-21:-1])/20)
            ma_60 = '%.2f' % (sum(df['close'][-61:-1])/60)
            ma_120 = '%.2f' % (sum(df['close'][-121:-1])/120)
            ma_240 = '%.2f' % (sum(df['close'][-241:-1])/240)
            volume = '%.2f' % (sum(df['volume'][-121:-1])/(len(df)-1))
            df['volume'][-7:-1]

            Session.add(Analysis(stock.id, amplitude, ma_5, ma_20, ma_60, ma_120, ma_240, volume))
            Session.commit()
            print(stock.id, ':', amplitude, ma_5, ma_20, ma_60, ma_120, ma_240, volume)
            #df['amplitude'] = (df['high']-df['low']) / df['close'].shift(1) * 100
            #amplitude = '%.2f' % (sum(df['amplitude'][-120:])/120)
            #row = Session.query(Analysis).filter_by(id=stock.id).first()
            #row.amplitude = amplitude
            #Session.commit()
            #print(stock.id, ':', amplitude)

#K_Means()

# a = [1,1,2,4,7]
# z1 = np.polyfit([1,2,3,4,5], [1,2,3,4,5],1)
# print(z1)
# p1= np.poly1d(z1)
# print(p1)

print(np.arange(1,5))