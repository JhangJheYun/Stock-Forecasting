import datetime
import psycopg2
import os
from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv

from routine import Add_Stock, Add_History, Add_Analysis
from utils import clustering


if __name__ == "__main__":

    load_dotenv()
    conn = psycopg2.connect(database = "teamc", 
                            user = os.getenv("user"), 
                            password = os.getenv("password"), 
                            host = os.getenv("host"), 
                            port = "5432")
    cur = conn.cursor()

    # Add_History:
    # cur.execute("SELECT * FROM stock")
    # stocks = cur.fetchall()
    # today = datetime.date.today()
    # tomorrow = today + datetime.timedelta(days = 1)
    # three_years_ago = today - relativedelta(years = 3)
    # for stock in stocks:
    #     Add_History(conn, cur, stock[0], three_years_ago.strftime('%Y%m%d'), tomorrow.strftime('%Y%m%d'))
    
    # Add_Analysis:
    # cur.execute("SELECT * FROM stock")
    # stocks = cur.fetchall()
    # for stock in stocks:
    #     Add_Analysis(conn, cur, stock[0])

    # output: [[low], [medium], [high]]
    stocks = clustering(conn, cur)

    cur.close()