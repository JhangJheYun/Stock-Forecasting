from flask import Flask, request
# from config import DevConfig
from flask import render_template
from datetime import date, timedelta
from stock_predict import get_high_low_prediction, get_k_line_info, get_stock_info, get_stock_name
from routine import Update_All_Analysis, Update_All_Stock, Is_latest, Get_Cluster_Stocks

app = Flask(__name__)
# app.run(debug = True)
# app.config.from_object(DevConfig)

@app.route('/')
def index():
    print('request type = ', request.method)
    is_latest = Is_latest()
    print(is_latest)
    return render_template('main.html', **locals())

@app.route('/twstock/cluster')
def cluster():
    low_risk_list, mid_risk_list, high_risk_list = Get_Cluster_Stocks()
    return render_template('stock_cluster.html', **locals())
    

@app.route('/twstock/update', methods = ['POST','GET'])
def update_data():
    if request.method == 'POST':
        Update_All_Stock()
        Update_All_Analysis()        
        return render_template('stock_predict.html')
    else :
        return render_template('update_stock.html')

@app.route('/twstock', methods = ['POST','GET'])
def html():
    if request.method == 'GET':
        if 'start_date' not in request.form:
            if 'stock_id' in request.args:
                stock_id = request.args.get('stock_id')
                stock_id = stock_id[-5:-1]
                print(stock_id)
            current_date = date.today() - timedelta(days = 1)
            start_date = current_date - timedelta(days = 366)
            print(start_date)
            
    
    if request.method == 'POST':
        start_date = request.form.get('start_date')
        model_type = request.form.get('model_type')
        stock_id = request.form.get('stock_id')
        stock_name = get_stock_name(stock_id)
        df_Stock = get_stock_info(stock_id, start_date)
        k_line_info = get_k_line_info(df_Stock)
        predict_high, predict_low = get_high_low_prediction(df_Stock, model_type)

    return render_template('stock_predict.html', **locals())



if __name__ == '__main__':
    # app = Flask(__name__)
    app.run(debug = True)