import requests
import pandas as pd
from config import Session
from schema import Stock, History
import datetime
from dateutil.relativedelta import relativedelta

def Connect_MM_DB(stock_id, start, end):
    data = requests.get('http://140.116.86.241:15000/api/v1/bargain_data/' + stock_id + '/' + start + '/' + end)
    return data.status_code, data.json()

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
    for index, data in df.iterrows():
        objects.append(dict(id = data['id'], name = data['name']))
    
    Session.bulk_insert_mappings(Stock, objects)
    Session.commit()

def Add_History(stock_id):
    
    today = datetime.date.today()
    two_days_ago = today - datetime.timedelta(days = 2)
    five_years_ago = today - relativedelta(years = 5)

    #stocks = Session.query(Stock).all()
    #for stock in stocks:
    status, data = Connect_MM_DB(str(stock_id), five_years_ago.strftime('%Y%m%d'), two_days_ago.strftime('%Y%m%d'))
    if status == 200:
        objects = list()
        for row in data:
            everyday = dict(id = row['stock_code_id'], date = datetime.datetime.utcfromtimestamp(int(row['date'])).strftime('%Y-%m-%d'), 
                            high = row['high'], low = data['low'], close = row['close'], volume = row['transaction_volume'])
            objects.append(everyday)
        Session.bulk_insert_mappings(History, everyday)
        Session.commit()
        print(stock_id, 'done.')
    else:
        print(stock_id, ' error.')

Add_History()