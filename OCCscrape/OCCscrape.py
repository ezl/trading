import time
import sys
import datetime
import sqlite3
import httplib2
import StringIO

def open_db():
    databasename = 'occDB.sqlite3'
    conn = sqlite3.connect(databasename)
    return conn

def create_table_if_not_exists(conn):
    sql = """CREATE TABLE IF NOT EXISTS occ (
                    quantity int,
                    underlying VARCHAR,
                    symbol VARCHAR,
                    actype VARCHAR,
                    porc VARCHAR(1),
                    exchange VARCHAR(10),
                    actdate TIMESTAMP)"""
    conn.cursor().execute(sql)

def query_occ(symbol, date):
    """
    Query optionsclearing.com data for given symbol and date, then return a CSV
    as a string.

    """
    http = httplib2.Http()
    url = 'http://optionsclearing.com/webapps/volume-query'
    headers = {
        'Content-type': 'application/x-www-form-urlencoded',
        'Referer': 'http://optionsclearing.com/webapps/volume-query'
    };
    data = 'volumeQuerySearch.volumeQueryType=O&volumeQuerySearch.symbolType=U&volumeQuerySearch.symbol={symbol}&volumeQuerySearch.futureSymbolType=ALL&volumeQuerySearch.futureSymbol=&volumeQuerySearch.dateRange=D&volumeQuerySearch.dailyDate={date}&volumeQuerySearch.weeklyDate=01%2F15%2F2010&volumeQuerySearch.monthDate=01%2F01%2F2010&volumeQuerySearch.fromDate=&volumeQuerySearch.toDate=&volumeQuerySearch.accountType=ALL&volumeQuerySearch.productKind=ALL&volumeQuerySearch.porc=BOTH&volumeQuerySearch.format=CSV&submit-query.x=84&submit-query.y=17'.format(symbol=symbol,date=date.replace('-','%2F'))
    response, content = http.request(url, 'POST', headers=headers, body=data)
    print "Getting data for {0} on {1}".format(symbol, date)
    return content

def insert_csv_to_sqlite3(conn, content):
    rows = content.strip().split("\n")
    if not len(rows) > 1:
        print "    No data. Skipped day."
        return
    data = [entry.strip().split(",") for entry in rows]
    data.pop(0)
    for entry in data:
        timeformat = time.strptime(entry[-1], "%m/%d/%Y")
        entry[-1] = datetime.date(*timeformat[:3])
        
    sql = """INSERT INTO occ(quantity, underlying, symbol, actype, porc, exchange, actdate) VALUES (?, ?, ?, ?, ?, ?, ?)"""
    conn.cursor().executemany(sql, data)

def bulk_grab_occ_data(symbol_list, date_list):
    for symbol in symbol_list:
        for date in date_list:
            csv =  query_occ(symbol, date.strftime("%m-%d-%Y"))
            insert_csv_to_sqlite3(conn, csv)

if __name__ == "__main__":
    conn = open_db()
    create_table_if_not_exists(conn)
    today = datetime.date.today()

    day = datetime.timedelta(days=1)
    query_duration = 365 * 1
    date_list = [today - n*day for n in range(query_duration)]
    symbol_list = ['XLF','FAS','FAZ']

    bulk_grab_occ_data(symbol_list=symbol_list, date_list=date_list)
    conn.commit() # close db
