import pandas as pd

df = pd.read_csv("C:\\Users\\Max\\orderbook.csv")
df['timestamp'] = pd.to_datetime(df['timestamp'])
#print(df.info())
#print(df.head())

def dbid(df, i):
    if df.loc[i, 'bid_price'] > df.loc[i-1, 'bid_price']:
        return df.loc[i, 'bid_size']
    elif df.loc[i, 'bid_price'] < df.loc[i-1, 'bid_price']:
        return - df.loc[i-1, 'bid_size']
    else:
        return df.loc[i, 'bid_size'] - df.loc[i-1, 'bid_size']
    
def dask(df, i):
    if df.loc[i, 'ask_price'] < df.loc[i-1, 'ask_price']:
        return - df.loc[i, 'ask_size']
    elif df.loc[i, 'ask_price'] > df.loc[i-1, 'ask_price']:
        return df.loc[i-1, 'ask_size']
    else:
        return df.loc[i, 'ask_size'] - df.loc[i-1, 'ask_size']
    
ofi = [0] + [dbid(df, i) - dask(df, i) for i in range(1, len(df))]
df['ofi'] = ofi

print(df.head(20))

import plotly.graph_objects as go

fig = go.Figure(data = go.Scatter(x=df['timestamp'], y=df['ofi']))

fig.show()