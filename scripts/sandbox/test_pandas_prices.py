import pandas_datareader as web
import datetime as dt

start = dt.datetime(2020,1,1)
end = dt.datetime.now()

ltc = web.DataReader('ROSE-USD', 'yahoo', start, end)
print(ltc)