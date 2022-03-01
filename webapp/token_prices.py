import pandas_datareader as web
import datetime as dt
from Historic_Crypto import HistoricalData

class CryptoOracle:

    def __init__(self, token):
        self.token = token
        self.pair = "{}-USD".format(self.token)

    def _stringify_datetime(self, dt):
        """nasty"""
        return "{}-{}-{}-{}-{}".format(dt.year, dt.month, dt.day, dt.hour, dt.minute)

    def get_token_price_df(self, startDate, endDate, interval_sec = 300):
        startDate = self._stringify_datetime(startDate)
        if endDate:
            endDate = self._stringify_datetime(endDate)
        
        if startDate and endDate:
            usd_pair_df = web.DataReader(self.pair, 'yahoo', startDate, endDate)
        if not endDate:
            usd_pair_df = web.DataReader(self.pair, 'yahoo', startDate, dt.today())

        if not len(usd_pair_df.index):
            print(f"\nMissing price info for {self.pair}")
        else:
            print("\nFound data for {}:".format(self.pair))
            print(usd_pair_df.head())
        return usd_pair_df


    def get_token_price_df_old(self, startDate, endDate, interval_sec = 300):
        """returns a dataframe containing price data for a given token
        given that Coinbase the price stored somewhere.
        Returns a dataframe:

        time                 low    high    open     close    volume                                                                     
        2021-12-22 00:05:00  2.3866  2.4054  2.4042  2.3884   61175.067550
        2021-12-22 00:10:00  2.3843  2.4003  2.3901  2.3987   51876.207316
        2021-12-22 00:15:00  2.3903  2.3997  2.3993  2.3975   44646.627470
        2021-12-22 00:20:00  2.3930  2.4088  2.3976  2.4049   45447.516436
        2021-12-22 00:25:00  2.4004  2.4091  2.4044  2.4070   22489.383224

        Args:
            startDate (datetime)
            endDate (datetime)
            interval_sec (int, optional): The time interval width in seconds of each price sample. Defaults to 300.
        """
        startDate = self._stringify_datetime(startDate)
        if endDate:
            endDate = self._stringify_datetime(endDate)
        
        if startDate and endDate:
            usd_pair_df = HistoricalData(self.pair, interval_sec, startDate, endDate).retrieve_data()
        elif not endDate:
            usd_pair_df = HistoricalData(self.pair, interval_sec, startDate).retrieve_data()
        
        print("\nFound data for {}:".format(self.pair))
        print(usd_pair_df.head())
        return usd_pair_df
