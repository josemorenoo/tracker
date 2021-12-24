from Historic_Crypto import HistoricalData
from datetime import datetime
#from Historic_Crypto import Cryptocurrencies
#from Historic_Crypto import LiveCryptoData

if __name__ == "__main__":
    #pairs = Cryptocurrencies(coin_search = 'LRC', extended_output=False).find_crypto_pairs()

    startDate = datetime(2021, 12, 20, 23, 25, 00)
    endDate = datetime(2021, 12, 20, 23, 30, 00)

    def _stringify_datetime(dt):
        """gross"""
        return "{}-{}-{}-{}-{}".format(dt.year, dt.month, dt.day, dt.hour, dt.minute)
    
    startDate = _stringify_datetime(startDate)
    endDate = _stringify_datetime(endDate)
    print(startDate)
    print(endDate)

    five_minute_interval = 300
    lrc_usd = HistoricalData('LRC-USD', five_minute_interval, startDate).retrieve_data()
    print(lrc_usd)