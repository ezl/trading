import datetime
import time
import sqlite3
import numpy as np
import pylab

def open_db():
    databasename = 'occDB.sqlite3'
    conn = sqlite3.connect(databasename)
    return conn

if __name__ == "__main__":
    symbol = 'XLF'
    conn = open_db()
    today = datetime.date.today()
    day = datetime.timedelta(days=1)
    cur = conn.cursor()

    startdate = today - 10 * day
    enddate = today - 5 * day
    startdate = datetime.date(2009,1,15)
    enddate = datetime.date(2010,2,15)
    symbol = symbol
    query_params = {'startdate':startdate, 'enddate':enddate, 'symbol':symbol,
                    'exchange':''}

    sql = """SELECT actdate, exchange, sum(quantity)
             FROM occ
             WHERE actdate > '%(startdate)s' AND
                   actdate < '%(enddate)s' AND
                   symbol LIKE '%(symbol)s'
             GROUP BY actdate, exchange
             ORDER BY actdate, exchange
             """
    cur.execute(sql % query_params)
    result = cur.fetchall()
    print "len(result):", len(result)
    for r in result:
        print r
    raw = np.array(result)
