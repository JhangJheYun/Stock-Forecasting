import math
import psycopg2
import heapq
import numpy as np
from sklearn.cluster import KMeans
from sklearn import preprocessing


def distance(info, center):

    info = np.array(info)
    center = np.array(center)
    value = np.sqrt(np.sum(np.square(info - center)))
    return value


def interval(ma, close):

    count = 0
    for daily in range(5):
        if close < ma[daily]:
            count += 1
    return count


def clustering(conn, cur):
    """ 挑出低中高三種風險的股票
        output已經sort過，[[低風險], [中風險], [高風險]]
        每個風險有五支股票，要取低風險第一就是stocks[0][0]
    """
    cur.execute("SELECT amplitude, close_trend, volume_trend, id, \
                ma_5, ma_20, ma_60, ma_120, ma_240, last_close FROM analysis")
    trend = cur.fetchall()
    trend = [[i[j] for j in range(10)] for i in trend]

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

    cluster_num = 10
    kmeans = KMeans(n_clusters=cluster_num).fit(normalize_trend)

    result = [0 for i in range(cluster_num)]
    for i in kmeans.labels_:
        result[i] += 1
    print('\nThe number of stocks in each classify :', result, '\n')
    print('Classify\tAmplitude\tClose_trend\tVolume_trend')

    for i in range(len(kmeans.labels_)):
        trend[i].append(kmeans.labels_[i])
    
    stock_id = [[] for _ in range(cluster_num)]
    info = [[0, 0, 0] for _ in range(cluster_num)]
    for i in range(cluster_num):
        for j in range(len(trend)):
            if trend[j][10] == i:
                stock_id[i].append(trend[j][3])
                for k in range(3):
                    info[i][k] += trend[j][k]
        for k in range(3):
            info[i][k] /= result[i]
        print(i, ',\t\t', '%.4f' % (info[i][0]), ',\t', '%.4f' % (info[i][1]), ',\t', '%.4f' % (info[i][2]))
    print()

    # map會return一個iterator，只能用一次
    top_index = map(result.index, heapq.nlargest(3, result))
    top_info = [(i, info[i][0]) for i in top_index]  # get top amplitude
    top_info = sorted(top_info, key = lambda x:x[1])
    top_index = map(result.index, heapq.nlargest(3, result))
    stock_list = dict([(i, stock_id[i]) for i in top_index])

    stocks = cluster_processing(top_info, stock_list, kmeans.cluster_centers_, trend)
    
    return stocks


def cluster_processing(rank, stock_list, center, info):

    # 加權越小越好
    # 都高於(0), 低於1~5條(1~5)
    weights = [[1, -1, -2, -3, -4, 0],
               [-3, -1, 0, 1, 2, 4],
               [-5, -2, 1, 2, 4, 10]]
    multiple = 50

    risk = ['low', 'mddium', 'high']
    stocks = []
    for index in range(len(rank)):

        classify = rank[index][0]
        temp = [i for i in stock_list[classify]]
        points = []  # [stock_id, moving_average(list), last_close, distance]
        for stock in temp:
            for row in info:
                if row[3] == stock:
                    points.append([stock, row[4:9], row[9], distance([i for i in row[:3]], center[classify])])
        points = sorted(points, key = lambda x:x[3])[:5]
        print('Candidates of ' + risk[index] + ' risk : ', end = '')

        for p in range(len(points)):
            count = interval(points[p][1], points[p][2])
            points[p][3] += (weights[index][count] * multiple)
        points = sorted(points, key = lambda x:x[3])

        stocks.append([i[0] for i in points])
        print([i[0] for i in points])

    return stocks
                

    


def analysis_error(conn, cur, stock_id):

    print(stock_id, 'data error', end='')

    # delete old data to avoid conflict
    cur.execute("DELETE FROM analysis WHERE id = " + str(stock_id))
    conn.commit()

    print(' ====> deleted.')
    

