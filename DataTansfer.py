import requests
import pandas as pd
import datetime
import time
import gc
import numpy as np
import psycopg2
import math
import heapq
import os
from io import StringIO
from config import Session
from schema import Stock, History
from dateutil.relativedelta import relativedelta
from sklearn.cluster import KMeans, AffinityPropagation, DBSCAN
from sklearn import preprocessing


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

        # objects = list()
        # for row in result:
        #     everyday = History(id = row['stock_code_id'], date = datetime.datetime.utcfromtimestamp(int(row['date'])).strftime('%Y-%m-%d'), 
        #                         high = row['high'], low = row['low'], close = row['close'], volume = row['capacity'])
        #     objects.append(everyday)

        # objects_key = [(i.id, i.date) for i in objects]
        # for row in Session.query(History.id, History.date):
        #     temp = (str(row[0]), row[1].strftime('%Y-%m-%d'))
        #     if temp in objects_key:
        #         index = objects_key.index(temp)
        #         del objects[index]
        #         del objects_key[index]

        # start = time.time()
        # Session.add_all(objects)
        # Session.commit()
        # end = time.time()
        # print(stock_id, 'done , time :', '{:.4f}'.format(end-start))

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

        close_trend = '%.4f' % (np.polyfit(np.arange(len(df['change'][-6:-1])), df['change'][-6:-1], 1)[-2])
        today_volume = list(df['volume'][-6:-1])
        yesterday_volume = list(df['volume'][-7:-1].shift(1))[1:]
        
        if len(today_volume) != len(yesterday_volume):
            print(stock_id)
            del today_volume[:len(today_volume) - len(yesterday_volume)]
        volume_subtract = [today_volume[i] - yesterday_volume[i] for i in range(len(today_volume))]

        volume_trend = '%.4f' % (np.polyfit(np.arange(len(volume_subtract)), volume_subtract, 1)[-2])

        cur.execute("INSERT INTO analysis(id, amplitude, ma_5, ma_20, ma_60, ma_120, ma_240, volume, close_trend, volume_trend)\
                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", 
                     (stock_id, amplitude, ma_5, ma_20, ma_60, ma_120, ma_240, volume, close_trend, volume_trend))
        conn.commit()
        print(stock_id, ':', amplitude, ma_5, ma_20, ma_60, ma_120, ma_240, volume, close_trend, volume_trend)

    else:
        print(stock_id, 'not exist in DB.')
        return

def clustering(conn, cur):
    # X = np.array([[1, 2], [2, 2], [2, 3],
    #               [8, 7], [8, 8], [25, 80]])
    cur.execute("SELECT amplitude, close_trend, volume_trend, id FROM Analysis")
    trend = cur.fetchall()
    trend = [[i[0], i[1], i[2], i[3]] for i in trend]

    amplitude = [0 if math.isnan(i[0]) else i[0] for i in trend]
    close = [i[1] for i in trend]
    volume = [i[2] for i in trend]
    for i in range(len(trend)):
        trend[i][0] = amplitude[i] 

    amplitude = preprocessing.normalize([amplitude])
    close = preprocessing.normalize([close])
    volume = preprocessing.normalize([volume])
    normalize_trend = trend.copy()
    for i in range(len(trend)):
        normalize_trend[i] = [amplitude[0][i], close[0][i], volume[0][i]]
    #print(normalize_trend)

    # x = np.array(trend)
    # cluster = DBSCAN().fit(x)
    # print(cluster)
    # print(cluster.labels_)
    # print(cluster.fit_predict([[0, 0], [2, 4]]))
    # for i in range(len(cluster.labels_)):
    #     if cluster.labels_[i] == 0:
    #         print(trend[i])

    
    #print(min(amplitude), max(amplitude), min(close), max(close), min(volume), max(volume))
    #print(min(amplitude[0]), max(amplitude[0]), min(close[0]), max(close[0]), min(volume[0]), max(volume[0]))
    cluster_num = 10
    kmeans = KMeans(n_clusters=cluster_num).fit(normalize_trend)
    #print(kmeans.labels_)

    result = [0 for i in range(cluster_num)]
    # for i in range(len(kmeans.labels_)):
    #     if kmeans.labels_[i] > 0:
    #         print(trend[i])
    for i in kmeans.labels_:
        result[i] += 1
    print('\nThe number of stocks in each classify :', result, '\n')
    print('Classify\tAmplitude\tClose_trend\tVolume_trend')

    for i in range(len(kmeans.labels_)):
        trend[i].append(kmeans.labels_[i])
    
    stock_id = [[] for _ in range(cluster_num)]
    for i in range(cluster_num):
        temp = [0, 0, 0]
        for j in range(len(trend)):
            if trend[j][4] == i:
                stock_id[i].append(trend[j][3])
                for k in range(3):
                    temp[k] += trend[j][k]
        print(i, ',\t\t', '%.4f' % (temp[0]/result[i]), ',\t', '%.4f' % (temp[1]/result[i]), ',\t', '%.4f' % (temp[2]/result[i]))
    
    # special = [2330, 2615, 4968, 8046, 2603]
    # for i in range(len(stock_id)):
    #     for s in special:
    #         if s in stock_id[i]:
    #             print(i, s)
    max_num_index_list = map(result.index, heapq.nlargest(3, result))
    for i in max_num_index_list:
        print(i, ':', stock_id[i])
    


if __name__ == "__main__":

    conn = psycopg2.connect(database="teamc", user=os.getenv("user"), password=os.getenv("password"), host=os.getenv("host"), port="5432")
    cur = conn.cursor()

    # Add_History()
    # cur.execute("SELECT * FROM stock")
    # stocks = cur.fetchall()
    # today = datetime.date.today()
    # tomorrow = today + datetime.timedelta(days = 1)
    # three_years_ago = today - relativedelta(years = 3)
    # for stock in stocks:
    #     Add_History(conn, cur, stock[0], three_years_ago.strftime('%Y%m%d'), today.strftime('%Y%m%d'))
    
    # Add_Analysis()
    # cur.execute("SELECT * FROM stock")
    # stocks = cur.fetchall()
    # for stock in stocks:
    #     Add_Analysis(conn, cur, stock[0])

    clustering(conn, cur)

    cur.close()