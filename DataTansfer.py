import requests
import pandas as pd
import datetime
import time
import gc
from config import Session
from schema import Stock, History
from dateutil.relativedelta import relativedelta

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

def Add_History(stock_id):
    
    today = datetime.date.today()
    three_years_ago = today - relativedelta(years = 3)

    #stocks = Session.query(Stock).all()
    #for stock in stocks:
    result = Connect_MM_DB(str(stock_id), three_years_ago.strftime('%Y%m%d'), today.strftime('%Y%m%d'))
    if type(result) != int :
        objects = list()
        for row in result:
            everyday = History(id = row['stock_code_id'], date = datetime.datetime.utcfromtimestamp(int(row['date'])).strftime('%Y-%m-%d'), 
                                high = row['high'], low = row['low'], close = row['close'], volume = row['transaction_volume'])
            objects.append(everyday)

        objects_key = [(i.id, i.date) for i in objects]
        for row in Session.query(History.id, History.date):
            temp = (str(row[0]), row[1].strftime('%Y-%m-%d'))
            if temp in objects_key:
                index = objects_key.index(temp)
                del objects[index]
                del objects_key[index]

        start = time.time()
        Session.add_all(objects)
        Session.commit()
        end = time.time()
        print(stock_id, 'done , time :', '{:.4f}'.format(end-start))

        del objects, objects_key, result
        gc.collect()
    else:
        print(stock_id, 'error :', result)





if __name__ == "__main__":

    stocks = Session.query(Stock).all()
    for stock in stocks:
        Add_History(stock.id)