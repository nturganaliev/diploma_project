import requests
import pandas as pd

def fetch_binance_data(symbol, interval='1h', limit=1000):
    base_url = 'https://api.binance.com/api/v3/klines'
    params = {
        'symbol': symbol,
        'interval': interval,
        'limit': limit
    }
    response = requests.get(base_url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data, columns=['open_time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
        df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
        df['close_time'] = pd.to_datetime(df['close_time'], unit='ms')
        df.set_index('open_time', inplace=True)
        return df
    else:
        print('Error fetching data:', response.status_code)
        return None

# Example usage:
btc_data = fetch_binance_data('BTCUSDT', interval='1d', limit=100)
print(btc_data.head())