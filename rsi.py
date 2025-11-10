import pandas as pd

df = pd.read_csv("C:\\Users\\Max\\orderbook.csv")
df['timestamp'] = pd.to_datetime(df['timestamp'])
#print(df.info())
#print(df.head())

def d_price(df):
    df['price'] = (df['bid_price'] + df['ask_price'])/2
    dp = [df.loc[i, 'price'] - df.loc[i-1, 'price'] for i in range(1, len(df))]
    return [dp[0]] + dp

df['delta_price'] = d_price(df)

# 3. Gain и Loss
df['gain'] = df['delta_price'].where(df['delta_price'] > 0, 0)
df['loss'] = (-df['delta_price']).where(df['delta_price'] < 0, 0)

# 4. Правильная функция EMA
def ema(values, period=14):
    alpha = 2 / (period + 1)
    ema_values = [values[0]]  # Первое значение
    for i in range(1, len(values)):
        ema_values.append(alpha * values[i] + (1 - alpha) * ema_values[i-1])
    return ema_values

df['avg_gain'] = ema(df['gain'])       
df['avg_loss'] = ema(df['loss'])    

df['rsi'] = (100 - (100 / (1 + df['avg_gain'] / df['avg_loss']))).where(df['avg_loss'] != 0, 100)

print(df.head(50))

import plotly.graph_objects as go

fig = go.Figure(data = go.Scatter(x=df['timestamp'], y=df['rsi']))

fig.show()