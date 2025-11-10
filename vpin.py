import pandas as pd

df = pd.read_csv("C:\\Users\\Max\\orderbook.csv")
df['timestamp'] = pd.to_datetime(df['timestamp'])
#print(df.info())
#print(df.head())

def calculate_vpin(df, volume_bucket_size=1000):
    """
    Расчет VPIN индикатора
    
    VPIN = |V_buy - V_sell| / V_total
    где V_buy - объем покупок, V_sell - объем продаж, V_total - общий объем
    
    Parameters:
    df: DataFrame с данными order book
    volume_bucket_size: размер объемного бакета для синхронизации
    """
    vpin_values = []
    
    # Рассчитываем объемы покупок и продаж на основе изменений в order book
    buy_volume = []
    sell_volume = []
    
    for i in range(len(df)):
        if i == 0:
            buy_vol = 0
            sell_vol = 0
        else:
            # Объем покупок: положительные изменения bid_size или уменьшение ask_size
            bid_change = df.loc[i, 'bid_size'] - df.loc[i-1, 'bid_size']
            ask_change = df.loc[i-1, 'ask_size'] - df.loc[i, 'ask_size']
            
            buy_vol = max(0, bid_change) + max(0, ask_change)
            
            # Объем продаж: положительные изменения ask_size или уменьшение bid_size
            sell_vol = max(0, ask_change) + max(0, -bid_change)
        
        buy_volume.append(buy_vol)
        sell_volume.append(sell_vol)
    
    df['buy_volume'] = buy_volume
    df['sell_volume'] = sell_volume
    
    # Создаем объемные бакеты
    cumulative_volume = 0
    bucket_buy_volume = 0
    bucket_sell_volume = 0
    bucket_count = 0
    
    for i in range(len(df)):
        cumulative_volume += df.loc[i, 'buy_volume'] + df.loc[i, 'sell_volume']
        bucket_buy_volume += df.loc[i, 'buy_volume']
        bucket_sell_volume += df.loc[i, 'sell_volume']
        
        if cumulative_volume >= volume_bucket_size or i == len(df) - 1:
            # Рассчитываем VPIN для текущего бакета
            total_volume = bucket_buy_volume + bucket_sell_volume
            if total_volume > 0:
                vpin = abs(bucket_buy_volume - bucket_sell_volume) / total_volume
            else:
                vpin = 0
            
            # Присваиваем значение VPIN всем записям в текущем бакете
            for j in range(bucket_count, i + 1):
                vpin_values.append(vpin)
            
            # Сбрасываем счетчики для следующего бакета
            cumulative_volume = 0
            bucket_buy_volume = 0
            bucket_sell_volume = 0
            bucket_count = i + 1
    
    return vpin_values

# Рассчитываем VPIN
vpin_values = calculate_vpin(df, volume_bucket_size=500)  # Используем меньший размер бакета для более детального анализа
df['vpin'] = vpin_values

import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Создаем график с двумя подграфиками
fig = make_subplots(
    rows=2, cols=1,
    subplot_titles=('OFI Indicator', 'VPIN Indicator'),
    vertical_spacing=0.1
)

# Добавляем OFI
fig.add_trace(
    go.Scatter(x=df['timestamp'], y=df['ofi'], name='OFI', line=dict(color='blue')),
    row=1, col=1
)

# Добавляем VPIN
fig.add_trace(
    go.Scatter(x=df['timestamp'], y=df['vpin'], name='VPIN', line=dict(color='red')),
    row=2, col=1
)

# Настройка осей
fig.update_xaxes(title_text="Time", row=2, col=1)
fig.update_yaxes(title_text="OFI", row=1, col=1)
fig.update_yaxes(title_text="VPIN", row=2, col=1)

# Настройка заголовка и размера
fig.update_layout(
    title="OFI и VPIN индикаторы для Bitcoin",
    height=800,
    showlegend=True
)

fig.show()