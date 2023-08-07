import pandas as pd
import os
print(os.getcwd())

df = pd.read_csv('./data/gmx_trade_pnl_2023-07-30.csv')
# df = df[df['time'] > '2023-05-01']

print(df.describe())


# pnl_pctg:
# min: -71
# mean: 20
# median: -1
# max: 2380
# std: 127