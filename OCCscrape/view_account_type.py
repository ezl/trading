import datetime
import time
import sqlite3
import numpy as np
import pylab
from scipy.signal import lfilter

def open_db():
    databasename = 'occDB.sqlite3'
    conn = sqlite3.connect(databasename)
    return conn

if __name__ == "__main__":
    conn = open_db()
    cur = conn.cursor()

    startdate = datetime.datetime.now().date() - datetime.timedelta(days=90)
    enddate = datetime.datetime.now().date()
    underlying_list = ['QQQQ',]
    query_params = {'startdate':startdate, 'enddate':enddate, 'underlying':'',
                    'account_type':''}
    account_type_list = ['C','M','F']

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
                        actype LIKE '%(account_type)s'
                  GROUP BY actdate
                  ORDER BY actdate) as volume
             ON date.actdate=volume.actdate
             """

    volume_data = {}
    for underlying in underlying_list:
        query_params['underlying'] = underlying
        for account_type in account_type_list:
            query_params['account_type'] = account_type
            cur.execute(sql % query_params)
            result = cur.fetchall()
            print result
            print account_type
            raw = np.array(result)
            volume_data[account_type] = {}
            volume_data[account_type]['quantity'] = raw[:,-1]
            volume_data[account_type]['quantity'] = np.array([float(i or 0) for i in
                                                    volume_data[account_type]['quantity']])
            volume_data[account_type]['date'] = [datetime.date(*time.strptime(r, "%Y-%m-%d")[:3]) for r in raw[:,0]]

        volume_data['TOTAL'] = {}
        volume_data['TOTAL']['date'] = volume_data['M']['date']
        volume_data['TOTAL']['quantity'] = sum(np.array([volume_data[account_type]['quantity'] for account_type in account_type_list]))

        # Percentages
        print account_type_list
        print volume_data['TOTAL']['date']
        for account_type in account_type_list:
            volume_data[account_type]['percent'] = volume_data[account_type]['quantity'] / volume_data['TOTAL']['quantity']

        window = 10
        for account_type in account_type_list:
            volume_data[account_type]['percent_moving_average'] = lfilter(np.ones(window), window, volume_data[account_type]['percent'])

        for account_type in account_type_list:
            pylab.plot(volume_data[account_type]['date'], volume_data[account_type]['percent_moving_average'], label=account_type)
            pylab.legend()
            pylab.xlabel('Date')
            pylab.ylabel('%s-day Weighted Average Percent Volume' % window)
            pylab.title(underlying)
        pylab.show()



