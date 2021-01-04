import requests
import pandas as pd
import datetime
import time
import gc
import numpy as np
# import psycopg2
import os
from io import StringIO
# from config import Session
from schema import Stock, History
from utils import analysis_error, clustering
from connect_database import connect_db
# from stock_predict import get_stock_name

def Get_Cluster_Stocks():
    """Get cluster of different risk stocks, 5 stocks each risk cluster """
    conn = connect_db()
    cur = conn.cursor()
    stocks = clustering(conn, cur)
    # cur.close()
    print(stocks)

    for risk_list in stocks:
        for idx, stock_id in enumerate(risk_list):
            cur.execute(f"select name from stock where id = {stock_id};")
            data = cur.fetchall()
            stock_name = str(data[0])
            stock_name = stock_name[2:-3]
            # stock_name = get_stock_name(stock_id)
            risk_list[idx] = stock_name + '(' + str(stock_id) + ')'
    cur.close()

    low_risk_list = stocks[0]
    mid_risk_list = stocks[1]
    high_risk_list = stocks[2]
    return low_risk_list, mid_risk_list, high_risk_list

def Is_latest():
    latest_date = get_latest_history_date()
    # today_week_day = datetime.date.weekday()
    # latest_week_day = latest_date.weekday()
    stock_id = '2330'
    start = (latest_date + datetime.timedelta(days = 1)).strftime('%Y%m%d')
    today = datetime.date.today()
    end = (today + datetime.timedelta(days = 1)).strftime('%Y%m%d')
    data = requests.get('http://140.116.86.241:15000/api/v1/bargain_data/' + f'{stock_id}' + '/' + f'{start}' + '/' + f'{end}')
    if data.status_code != 200:
        return True
    else:
        return False 

def get_latest_history_date():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute('SELECT date FROM history WHERE id = 2330 ORDER BY date DESC LIMIT 1 ;')
    latest_date = cur.fetchall()[0][0]
    cur.close()
    print(latest_date)
    return latest_date

def Update_All_Stock():
    """Update history info of all stocks"""
    conn = connect_db()
    cur = conn.cursor()
    cur.execute('SELECT id FROM stock;')
    stocks = cur.fetchall()
    today = datetime.date.today()
    tomorrow = today + datetime.timedelta(days = 1)
    # three_years_ago = today - relativedelta(years = 3)
    latest_date = get_latest_history_date() + datetime.timedelta(days = 1)

    for stock in stocks:
        Add_History(conn, cur, stock[0], latest_date.strftime('%Y%m%d'), tomorrow.strftime('%Y%m%d'))
    cur.close()
    print('Update all stock history success')

def Update_All_Analysis():
    """Update analysis info of all stocks"""
    conn = connect_db()
    cur = conn.cursor()
    cur.execute('SELECT * FROM stock;')
    stocks = cur.fetchall()

    for stock in stocks:
        Add_Analysis(conn, cur, stock[0])
    cur.close()
    print('Update all analysis success')

def Connect_MM_DB(stock_id, start, end):
    data = requests.get('http://140.116.86.241:15000/api/v1/bargain_data/' + stock_id + '/' + start + '/' + end)
    return data.json() if data.status_code == 200 else data.status_code

def Add_Stock():
    res = requests.get('http://isin.twse.com.tw/isin/C_public.jsp?strMode=2')
    df = pd.read_html(res.text)[0]
    df = df.drop([0, 1]).reset_index()  # 刪除"股票"列
    df = df.drop('index', axis=1)
    df = df.iloc[:946, :1]              # 946列是股票9958最後一檔
    df[0] = df[0].map(lambda x: x.replace(' ', '　'))
    df['id'] = df[0].map(lambda x: x.split('　')[0])
    df['name'] = df[0].map(lambda x: x.split('　')[1])

    objects = list()
    for _, data in df.iterrows():
        objects.append(dict(id = data['id'], name = data['name']))
    
    Session.bulk_insert_mappings(Stock, objects)
    Session.commit()

def Add_History(conn, cur, stock_id, start, end):

    result = Connect_MM_DB(str(stock_id), start, end)
    if type(result) != int :

        f = StringIO()
        for row in result:
            f.write(str(row['stock_code_id']) + '\t' + 
                    datetime.datetime.utcfromtimestamp(int(row['date'])).strftime('%Y-%m-%d') + '\t' + 
                    str(row['high']) + '\t' + str(row['low']) + '\t' + 
                    str(row['close']) + '\t' + str(row['capacity']) + '\t' + 
                    str(row['open']) + '\t' + str(row['change']) + '\n')
        f.seek(0)
        start = time.time()
        cur.copy_from(f, 'history',
                      columns=('id', 'date', 'high', 'low', 'close', 'volume', 'open', 'change'), 
                      sep='\t', null='\\N')
        conn.commit()
        end = time.time()
        print(stock_id, 'done , time :', '{:.4f}'.format(end-start))

        del result
        gc.collect()
    else:
        print(stock_id, 'error :', result)

def Add_Analysis(conn, cur, stock_id):

    #trans = Session.query(History).filter(stock_id == History.id).all()
    cur.execute("SELECT * FROM history WHERE id = " + str(stock_id))
    query = cur.fetchall()
    if len(query) != 0 :
        df = pd.DataFrame([(i[0], i[1].strftime('%Y-%m-%d'), i[2], i[3], i[4], i[5], i[6], i[7]) for i in query], 
                          columns=['id', 'date', 'high', 'low', 'close', 'volume', 'open', 'change'])
        df = df.set_index('date')
        df = df.sort_values(['date'])

        df['amplitude'] = (df['high']-df['low']) / df['close'].shift(1) * 100
        amplitude = '%.4f' % (sum(df['amplitude'][-121:-1])/120)
        ma_5 = '%.4f' % (sum(df['close'][-6:-1])/5)
        ma_20 = '%.4f' % (sum(df['close'][-21:-1])/20)
        ma_60 = '%.4f' % (sum(df['close'][-61:-1])/60)
        ma_120 = '%.4f' % (sum(df['close'][-121:-1])/120)
        ma_240 = '%.4f' % (sum(df['close'][-241:-1])/240)
        volume = '%.4f' % (sum(df['volume'][-121:-1])/(len(df)-1))
        last_close = df['close'][-1]

        if len(df['change'][-6:-1]) != 5:
            analysis_error(conn, cur, stock_id)
            return

        close_trend = '%.4f' % (np.polyfit(np.arange(len(df['change'][-6:-1])), df['change'][-6:-1], 1)[-2])
        today_volume = list(df['volume'][-6:-1])
        yesterday_volume = list(df['volume'][-7:-1].shift(1))[1:]
        
        if len(today_volume) != len(yesterday_volume):
            analysis_error(conn, cur, stock_id)
            return

        volume_subtract = [today_volume[i] - yesterday_volume[i] for i in range(len(today_volume))]
        volume_trend = '%.4f' % (np.polyfit(np.arange(len(volume_subtract)), volume_subtract, 1)[-2])

        cur.execute("INSERT INTO analysis(id, amplitude, ma_5, ma_20, ma_60, ma_120, ma_240, volume, close_trend, volume_trend, last_close)\
                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) \
                     ON CONFLICT (id) DO UPDATE \
                        SET (amplitude, ma_5, ma_20, ma_60, ma_120, ma_240, volume, close_trend, volume_trend, last_close) = \
                            (EXCLUDED.amplitude, EXCLUDED.ma_5, EXCLUDED.ma_20, EXCLUDED.ma_60, EXCLUDED.ma_120, EXCLUDED.ma_240, \
                             EXCLUDED.volume, EXCLUDED.close_trend, EXCLUDED.volume_trend, EXCLUDED.last_close)", 
                     (stock_id, amplitude, ma_5, ma_20, ma_60, ma_120, ma_240, volume, close_trend, volume_trend, last_close))
        conn.commit()
        print(stock_id, ':', amplitude, ma_5, ma_20, ma_60, ma_120, ma_240, volume, close_trend, volume_trend, last_close)

    else:
        print(stock_id, 'not exist in DB.')
        return