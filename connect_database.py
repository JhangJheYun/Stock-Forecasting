import psycopg2
from config import config

def connect_db():
    """ Connect to PostgreSQL database server """
    conn = None
    try:
        params = config()
        print('Connecting to PostgreSQL database from AWS RDS . . .')
        # conn = psycopg2.connect(host = 'twstock-database.ctaidhzjqlwd.us-east-1.rds.amazonaws.com', database = 'postgres', user = 'netdb602', password = 'netdb2602', port = '5432')
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        print('PostgreSQL database version : ') 
        cur.execute('SELECT version()')
        db_version = cur.fetchone()
        print(db_version) 
        cur.close()
    except (Exception, psycopg2.DatabaseError) as err:
        print(err)
    return conn  


if __name__ == '__main__':
    print('Program Activated')
    # conn = connect_db()
    # try :
    #     cur = conn.cursor()
    #     cur.execute('select * from test;')
    #     rows = cur.fetchall()
    #     df = pd.DataFrame(rows, columns = ['stock_id'])
    #     print(df)
    # except Exception as err:
    #     print(err)
    # finally:
    #     if conn is not None:
    #         conn.close()
    #         print('Database connection closed .')

    