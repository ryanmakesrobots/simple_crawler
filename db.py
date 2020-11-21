import pymysql

def new_conn():
    conn = pymysql.connect(
        host='',
        user='',
        password='',
        db='')
    c = conn.cursor()
    return conn, c
