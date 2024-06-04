# app.py
from flask import Flask, render_template, request
import pandas as pd
import numpy as np
from tensorflow import keras
from keras.models import Sequential
from keras.layers import LSTM, Dense
from binance.client import Client

app = Flask(__name__)
client = Client(api_key='kSQW3nMBJTq74IpX8QCtty0rR6KqLynKStKD2g79DWWIXamgB8oFgt3eaCon7NBB', api_secret='z4CjRRTip1davAM84qEwWR6GCvvLRQyEq0KE3k4zHp0mi1bKNecn1MiHbrZTeHG7')

def get_cryptocurrency_data(symbol, time_frame):
    klines = client.get_klines(symbol=symbol, interval=time_frame)
    df = pd.DataFrame(klines, columns=['Open Time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close Time', 'Quote Asset Volume', 'Number of Trades', 'Taker Buy Base Asset Volume', 'Taker Buy Quote Asset Volume', 'Ignore'])
    df['Open Time'] = pd.to_datetime(df['Open Time'], unit='ms')
    df.set_index('Open Time', inplace=True)
    df['Close'] = pd.to_numeric(df['Close'], errors='coerce')
    # Ensure 'Open Time' is datetime
    # df['Open Time'] = pd.to_datetime(df['Open Time'], unit='ms')
    return df['Close']

def prepare_data(series, n_steps):
    X, y = [], []
    for i in range(len(series)):
        end_ix = i + n_steps
        if end_ix > len(series)-1:
            break
        seq_x, seq_y = series[i:end_ix], series[end_ix]
        X.append(seq_x)
        y.append(seq_y)
    return np.array(X), np.array(y)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        symbol = request.form['symbol']
        time_frame = request.form['time_frame']
        data = get_cryptocurrency_data(symbol, time_frame)
        n_steps = 3  # adjust as needed
        X, y = prepare_data(data.values, n_steps)
        X = X.reshape((X.shape[0], X.shape[1], 1))
        model = Sequential()
        model.add(LSTM(50, activation='relu', input_shape=(n_steps, 1)))
        model.add(Dense(1))
        model.compile(optimizer='adam', loss='mse')
        model.fit(X, y, epochs=200, verbose=0)
        last_data = data[-n_steps:].values.reshape((1, n_steps, 1))
        prediction = model.predict(last_data)[0][0]
        return render_template('index.html', prediction=prediction)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
