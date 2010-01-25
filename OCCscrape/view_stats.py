import datetime
import time
import sqlite3
import numpy as np
import pylab

def open_db():
    databasename = 'occDB.sqlite3'
    conn = sqlite3.connect(databasename)
    return conn

def get_exchanges(query_params):
    sql = """SELECT DISTINCT exchange
             FROM occ
             WHERE actdate > '%(startdate)s' AND
                   actdate < '%(enddate)s' AND
                   underlying LIKE '%(underlying)s'
            """
    cur.execute(sql % query_params)
    result = cur.fetchall()
    return [r[0] for r in result]

if __name__ == "__main__":
    conn = open_db()
    cur = conn.cursor()

    startdate = datetime.date(2009,1,10)
    enddate = datetime.date(2010,1,13)
    underlying = 'XLF'
    query_params = {'startdate':startdate, 'enddate':enddate, 'underlying':underlying,
                    'exchange':''}
    exchange_list = get_exchanges(query_params)

    sql = """SELECT date.actdate, volume.sum FROM
                 (SELECT DISTINCT actdate
                  FROM occ
                  WHERE actdate >= '%(startdate)s' AND
                      actdate < '%(enddate)s' AND
                      underlying LIKE '%(underlying)s') as date
             LEFT OUTER JOIN
                 (SELECT actdate, sum(quantity) as sum
                  FROM occ
                  WHERE actdate >= '%(startdate)s' AND
                        actdate < '%(enddate)s' AND
                        underlying LIKE '%(underlying)s' AND
                        exchange LIKE '%(exchange)s'
                  GROUP BY actdate
                  ORDER BY actdate) as volume
             ON date.actdate=volume.actdate
             """

    volume_data = {}
    for exchange in exchange_list:
        query_params['exchange'] = exchange
        cur.execute(sql % query_params)
        result = cur.fetchall()
        print "%s len(result): %s" % (exchange, str(len(result)))
        print result
        print "*" * 30
        print
        raw = np.array(result)
        volume_data[exchange] = {}
        volume_data[exchange]['quantity'] = raw[:,-1]
        volume_data[exchange]['quantity'] = np.array([float(i or 0) for i in
                                            volume_data[exchange]['quantity']])
        volume_data[exchange]['date'] = [datetime.date(*time.strptime(r, "%Y-%m-%d")[:3]) for r in raw[:,0]]

    volume_data['TOTAL'] = {}
    volume_data['TOTAL']['date'] = volume_data['ISE']['date']
    volume_data['TOTAL']['quantity'] = sum(np.array([volume_data[exchange]['quantity'] for exchange in exchange_list]))

    # Percentages
    print exchange_list
    print volume_data['TOTAL']['date']

    for exchange in exchange_list:
        volume_data[exchange]['percent'] = volume_data[exchange]['quantity'] / volume_data['TOTAL']['quantity']
        print volume_data[exchange]['percent']

    for exchange in exchange_list:
        pylab.plot(volume_data[exchange]['date'], volume_data[exchange]['percent'], label=exchange)
    pylab.legend()
    pylab.show()



