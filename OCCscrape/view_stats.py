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

    def get_exchanges(query_params):
        sql = """SELECT DISTINCT exchange
                 FROM occ
                 WHERE actdate > '%(startdate)s' AND
                       actdate < '%(enddate)s' AND
                       symbol LIKE '%(symbol)s'
                """
        cur.execute(sql % query_params)
        result = cur.fetchall()
        return [r[0] for r in result]

    exchange_list = get_exchanges(query_params)

    sql = """SELECT actdate, exchange, sum(quantity)
             FROM occ
             WHERE actdate > '%(startdate)s' AND
                   actdate < '%(enddate)s' AND
                   symbol LIKE '%(symbol)s' AND
                   exchange LIKE '%(exchange)s'
             GROUP BY actdate
             ORDER BY actdate
             """
    volume_data = {}
    for exchange in exchange_list:
        query_params['exchange'] = exchange
        cur.execute(sql % query_params)
        result = cur.fetchall()
        print "len(result):", len(result)
        raw = np.array(result)
        volume_data[exchange] = {}
        volume_data[exchange]['quantity'] = raw[:,-1]
        volume_data[exchange]['date'] = [datetime.date(*time.strptime(r, "%Y-%m-%d")[:3]) for r in raw[:,0]]

    
    for exchange in exchange_list:
        pylab.plot(volume_data[exchange]['date'],volume_data[exchange]['quantity'], label=exchange)
    pylab.legend()
    pylab.show()

#    data = {}
#    labels = ['quantity', 'underlying', 'symbol', 'actype', 'porc',
#              'exchange', 'actdate']
#    for i, label in enumerate(labels):
#        data[label] = raw[:,i]
#    print data
#    print "^"*40
#    print type(data['actdate'][5])
#    print data['actdate'][5]
#    print "^"*40
#    pylab.plot(range(len(data['actdate'])), data['quantity'])
#    pylab.show()
