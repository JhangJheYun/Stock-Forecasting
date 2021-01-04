import numpy as np
import os
import time
import pandas as pd
from datetime import datetime

from keras.models import Sequential
from keras.layers import Dense, LSTM, TimeDistributed
from keras.layers.normalization import BatchNormalization
from keras.optimizers import Adam
from keras.callbacks import EarlyStopping
# import matplotlib.pyplot as plt

current_year = datetime.now().year
current_month = datetime.now().month

def read_from_api(stock_id, start_year, start_month, end_year, end_month):
  stock = twstock.Stock(stock_id)
  st_lst = []
#   current_year = datetime.now().year
#   current_month = datetime.now().month
  for year in range(start_year, end_year + 1,1):
    if year != start_year:
      start_month = 1
    for i in range(start_month, 13, 1):
      if year == current_year and (i == current_month + 1):break
      if year == end_year and i == end_month : break
      stock_info = stock.fetch(year,i)
      st_lst += stock_info
      time.sleep(10)
  df = pd.DataFrame(st_lst)
  # df = df[['date', 'open', 'high', 'low', 'close', 'capacity']]
  return df

def readTrain(file_name = '', stock_id = '2330', start_year = current_year - 1, start_month = 1, end_year = current_year, end_month = current_month):
  if os.path.exists(file_name):
    train = pd.read_csv(file_name)
  else:
    train = read_from_api(stock_id)
#   train = train[['date', 'open', 'high', 'low', 'close', 'volume']]
  train = train[['date', 'high', 'low', 'close', 'volume']]
  return train

def augFeatures(train):
  train["date"] = pd.to_datetime(train["date"])
  train["year"] = train["date"].dt.year.astype('float64')
  train["month"] = train["date"].dt.month.astype('float64')
  train["day"] = train["date"].dt.day
  train["dayofweek"] = train["date"].dt.dayofweek
  train = train.drop(["date"], axis=1)
  return train

def normalize(train):
  train_norm = train.apply(lambda x: (x - np.mean(x)) / (np.max(x) - np.min(x)))
  return train_norm

def buildTrain(train, pastDay, futureDay, label = 'close'):
  X_train, Y_train = [], []
  for i in range(train.shape[0]-futureDay-pastDay):
    X_train.append(np.array(train.iloc[i:i+pastDay]))
    if label != '':
      Y_train.append(np.array(train.iloc[i+pastDay:i+pastDay+futureDay][label]))
    else:
      Y_train.append(np.array(train.iloc[i+pastDay:i+pastDay+futureDay]))
  return np.array(X_train), np.array(Y_train)

def shuffle(X,Y):
  np.random.seed(10)
  randomList = np.arange(X.shape[0])
  np.random.shuffle(randomList)
  return X[randomList], Y[randomList]

def splitData(X,Y,rate):
  X_train = X[int(X.shape[0]*rate):]
  Y_train = Y[int(Y.shape[0]*rate):]
  X_val = X[:int(X.shape[0]*rate*(1/3))]
  Y_val = Y[:int(Y.shape[0]*rate*(1/3))]
  X_test = X[int(X.shape[0]*rate*(1/3)):int(X.shape[0]*rate)]
  Y_test = Y[int(Y.shape[0]*rate*(1/3)):int(Y.shape[0]*rate)]
  return X_train, Y_train, X_val, Y_val, X_test, Y_test

# 一對一預測
def buildOneToOneModel(shape, X_train, Y_train, X_val, Y_val):
 # from 2 dimmension to 3 dimension
  Y_train = Y_train[:,np.newaxis]
  Y_val = Y_val[:,np.newaxis]

  model = Sequential()
  model.add(LSTM(30, input_length=shape[1], input_dim=shape[2],return_sequences=True))
  print('shape[1] = ', shape[1])
  print('shape[2] = ', shape[2])
  # output shape: (1, 1)
  model.add(TimeDistributed(Dense(1)))    # or use model.add(Dense(1))
  # model.add((Dense(1))) 
  model.compile(loss="mse", optimizer="adam")
  model.summary()
  callback = EarlyStopping(monitor="loss", patience=10, verbose=0, mode="auto")
  model.fit(X_train, Y_train, epochs=1000, batch_size=128, validation_data=(X_val, Y_val), callbacks=[callback])
  return model

# 多對一預測
def buildManyToOneModel(shape, X_train, Y_train, X_val, Y_val):
  model = Sequential()
  model.add(LSTM(30, input_length=shape[1], input_dim=shape[2]))
  print('shape[1] = ', shape[1])
  print('shape[2] = ', shape[2])
  # output shape: (1, 1)
  model.add(Dense(1))
  model.compile(loss="mse", optimizer="adam")
  model.summary()
  callback = EarlyStopping(monitor="loss", patience=10, verbose=0, mode="auto")
  model.fit(X_train, Y_train, epochs=1000, batch_size=128, validation_data=(X_val, Y_val), callbacks=[callback])
  return model

# 多對多預測
def buildManyToManyModel(shape, X_train, Y_train, X_val, Y_val):
  # from 2 dimmension to 3 dimension
  Y_train = Y_train[:,:,np.newaxis]
  Y_val = Y_val[:,:,np.newaxis]
  
  model = Sequential()
  model.add(LSTM(30, input_length=shape[1], input_dim=shape[2], return_sequences=True))
  print('shape[1] = ', shape[1])
  print('shape[2] = ', shape[2])
  # output shape: (5, 1)
  model.add(TimeDistributed(Dense(1)))
  model.compile(loss="mse", optimizer="adam")
  model.summary()
  callback = EarlyStopping(monitor="loss", patience=10, verbose=0, mode="auto")
  model.fit(X_train, Y_train, epochs=1000, batch_size=128, validation_data=(X_val, Y_val), callbacks=[callback])
  return model
