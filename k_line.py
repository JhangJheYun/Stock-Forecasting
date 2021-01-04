# basic
import numpy as np
import pandas as pd

# # get data
# import pandas_datareader as pdr

# visual
import matplotlib.pyplot as plt
import mpl_finance as mpf
import seaborn as sns

# #time
# import datetime as datetime

#talib
import talib


def draw_k_line(df_Stock):
    sma_5 = talib.SMA(np.array(df_Stock['close']), 5) 
    sma_10 = talib.SMA(np.array(df_Stock['close']), 10)
    sma_30 = talib.SMA(np.array(df_Stock['close']), 30)

    fig = plt.figure(figsize=(24, 20))
    ax = fig.add_axes([0,0.3,1,0.4])

    ax.set_xticks(range(0, len(df_Stock.index), 1))
    ax.set_xticklabels(df_Stock.index[::])
    mpf.candlestick2_ochl(ax, df_Stock['open'], df_Stock['close'], df_Stock['high'],
                        df_Stock['low'], width=0.6, colorup='r', colordown='g', alpha=0.75)
    plt.rcParams['font.sans-serif']=['Microsoft JhengHei'] 
    ax.plot(sma_5, label='5日均線')
    ax.plot(sma_10, label='10日均線')
    ax.plot(sma_30, label='30日均線')
    plt.xticks(rotation = 90)
    plt.grid()


    ax.legend()

    plt.savefig('static/media/k_line.png')

def draw_kd_line(df_Stock):
    df_Stock['k'], df_Stock['d'] = talib.STOCH(df_Stock['high'], df_Stock['low'], df_Stock['close'])
    df_Stock['k'].fillna(value=0, inplace=True)
    df_Stock['d'].fillna(value=0, inplace=True)

    fig = plt.figure(figsize=(24, 20))
    ax2 = fig.add_axes([0,0.2,1,0.1])

    ax2.plot(df_Stock['k'], label='K值')
    ax2.plot(df_Stock['d'], label='D值')
    ax2.set_xticks(range(0, len(df_Stock.index), 1))
    ax2.set_xticklabels(df_Stock.index[::])
    plt.xticks(rotation = 90)
    plt.grid()

    ax2.legend()
    plt.savefig('static/media/kd_line.png')

def draw_volume(df_Stock):
    fig = plt.figure(figsize=(24, 20))
    ax3 = fig.add_axes([0,0,1,0.2])

    mpf.volume_overlay(ax3, df_Stock['open'], df_Stock['close'], df_Stock['volume'], colorup='r', colordown='g', width=0.5, alpha=0.8)
    ax3.set_xticks(range(0, len(df_Stock.index), 1))
    ax3.set_xticklabels(df_Stock.index[::])
    plt.xticks(rotation = 90)
    plt.grid()

    plt.savefig('static/media/volume.png')

