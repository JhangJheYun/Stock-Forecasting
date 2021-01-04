from connect_database import connect_db
import pandas as pd
import numpy as np
from lstm import readTrain, augFeatures, normalize, buildTrain, splitData, shuffle\
, buildManyToOneModel, buildOneToOneModel, buildManyToManyModel
from gru import gru_predict_price
from sklearn.metrics import mean_squared_error
# from k_line import draw_k_line, draw_kd_line, draw_volume

def get_stock_info(stock_id, start_date):
    """ Get stock information  """
    conn = connect_db()
    cur = conn.cursor()
    cur.execute(f"select * from history where id = {stock_id} and date >= '{start_date}' ;")
    data = cur.fetchall()
    cur.close()
    stock_df = pd.DataFrame(data, columns = ['id', 'date', 'high', 'low', 'close', 'volume', 'open', 'change'])
    stock_df = stock_df.sort_values(by=['date'])
    # stock_id = stock_df['id'].iloc[0]
    return stock_df

def get_stock_name(stock_id):
    """ Get stock name  """
    conn = connect_db()
    cur = conn.cursor()
    cur.execute(f"select name from stock where id = {stock_id};")
    data = cur.fetchall()
    cur.close()
    
    stock_name = str(data[0])
    stock_name = stock_name[2:-3]
    return stock_name

def predict_price(stock_df, model_type, target_label, past_days, future_days):
    # train_df = readTrain('TSCM_origin_2010_to_2020_10.csv')
    # stock_id = stock_df['id'].iloc[0]
    stock_df = stock_df.drop(["id"], axis=1)
    train_df = augFeatures(stock_df)
    origin_df = train_df.copy()
    train_df = normalize(train_df)
    
    # change the last day and next day 
    X_train, Y_train = buildTrain(train_df, past_days, future_days, target_label)
    X_train, Y_train = shuffle(X_train, Y_train)
    # because no return sequence, Y_train and Y_val shape must be 2 dimension
    X_train, Y_train, X_val, Y_val, X_test, Y_test = splitData(X_train, Y_train, 0.3)
    
    if model_type == 'MtO':
        model = buildManyToOneModel(X_train.shape, X_train, Y_train, X_val, Y_val)
    elif model_type == 'OtO':
        model = buildOneToOneModel(X_train.shape, X_train, Y_train, X_val, Y_val)
    else :
        model = buildManyToManyModel(X_train.shape, X_train, Y_train, X_val, Y_val)
    
    target_price = get_real_price(train_df, origin_df, model, model_type, target_label, past_days)
    mse = get_mean_square_error(model, model_type, X_test, Y_test)
    return target_price, mse

def get_real_price(train_df, origin_df, model, model_type, target_label, past_days):
    stock_test = np.array(train_df.iloc[-past_days:])
    stock_test = stock_test.reshape((1,past_days,-1))
    pre = model.predict(stock_test)
    pre.tolist()
    target_price_ser = (origin_df[target_label])
    # print(pre)

    # Many to One
    if model_type == 'MtO': 
        pre = pre[0][0]
        target_price = pre * (np.max(target_price_ser) - np.min(target_price_ser)) + np.mean(target_price_ser)
    
    #One to One
    elif model_type == 'OtO':
        pre = pre[0][0][0]
        target_price = pre * (np.max(target_price_ser) - np.min(target_price_ser)) + np.mean(target_price_ser)
    
    # Many to Many
    else :
        target_price = []
        for i in range(past_days):
            pre_temp = pre[0][i][0]
            target_price.append(pre_temp * (np.max(target_price_ser) - np.min(target_price_ser)) + np.mean(target_price_ser))
    
    return target_price

def get_k_line_info(df_Stock):
    df_Stock.astype({'date': 'str'})
    stock_info_list = df_Stock.values.tolist()
    return stock_info_list


def get_high_low_prediction(df_Stock, model_type = 'OtO' ):
    if model_type == 'MtM':
        MtM_price_h, mse_h = predict_price(df_Stock, 'MtM', 'high', 5, 5)
        MtM_price_l, mse_l = predict_price(df_Stock, 'MtM', 'low', 5, 5)
        print(MtM_price_l, ' - ',MtM_price_h ,'\n', mse_l ,' - ',mse_h)
        return round(MtM_price_h[0], 2), round(MtM_price_l[0], 2)
    elif model_type == 'MtO':
        MtO_price_h, mse_h = predict_price(df_Stock, 'MtO', 'high', 30, 1)
        MtO_price_l, mse_l = predict_price(df_Stock, 'MtO', 'low', 30, 1)
        print(MtO_price_l, ' - ',MtO_price_h ,'\n', mse_l ,' - ',mse_h)
        return round(MtO_price_h, 2), round(MtO_price_l, 2)
    elif model_type == 'OtO' :
        OtO_price_h, mse_h = predict_price(df_Stock, 'OtO','high', 1, 1)
        OtO_price_l, mse_l = predict_price(df_Stock, 'OtO', 'low', 1, 1)
        print(OtO_price_l, ' - ', OtO_price_h ,'\n', mse_l ,' - ',mse_h)
        return round(OtO_price_h, 2), round(OtO_price_l, 2)
    else :
        GRU_price_h, mse_h = gru_predict_price(df_Stock, 'high')
        GRU_price_l, mse_l = gru_predict_price(df_Stock, 'low')
        print(GRU_price_l, ' - ',GRU_price_h ,'\n', mse_l ,' - ',mse_h)
        return round(GRU_price_h,2), round(GRU_price_l, 2)


def get_mean_square_error(model, model_type, X_test, Y_test):
    pre = model.predict(X_test)
    if model_type == 'MtM':
        pre = pre.reshape(-1,5)
    else :
        pre = pre.reshape(-1,1)
    
    print(pre.shape)
    print(Y_test.shape)
    mse = mean_squared_error(pre, Y_test)
    print(mse)
    return mse