import pandas as pd
import json


def max_by_column(df, groupby_name, max_name, sort=False):
    idx = df.groupby([groupby_name], sort=sort)[max_name].transform(max) == df[max_name]
    return df[idx]


def min_by_column(df, groupby_name, min_name, sort=False):
    idx = df.groupby([groupby_name], sort=sort)[min_name].transform(min) == df[min_name]
    return df[idx]


df = pd.read_csv('bids.csv')

df['AAV'] = df['Total'] / df['Years']
df['Y1'] = pd.to_numeric(df['Breakdown'].str.split(",", n=1, expand=True)[0]).fillna(df['AAV'])
# max_order = df['Order'].max()
# df['Reverse Order'] = max_order - df.loc[:, 'Order']

teams = df['Team'].unique()
players = df['Player'].unique()

df = max_by_column(df, 'Player', 'AAV')
df = max_by_column(df, 'Player', 'Years')
df = max_by_column(df, 'Player', 'Y1')
df = min_by_column(df, 'Player', 'Order')
df.drop('Y1', axis=1, inplace=True)

teams = df.Team.unique()
players = df.Player.unique()
winning_bids = {}
width = 2
precision = 4

with open('test.txt', 'w') as f:
    for team in teams:
        f.write(f'[b][u]{team}[/u][/b]\n')
        winning_df = df.loc[df['Team'] == team]
        for idx, row in winning_df.iterrows():
            year_string = 'year' if row.Years == 1 else 'years'
            f.write(f'{row.Player}, {row.Years} {year_string} at {row.AAV:{width}.{precision}}/year\n')
        winning_df.set_index('Player', inplace=True)
        f.write('\n')

for player in players:
    winning_df = df.loc[df['Player'] == player].drop(['Player', 'Order'], axis=1)
    winning_df.set_index('Team', inplace=True)
    winning_bids[player] = winning_df.transpose().to_json()

with open('temp_bids.json', 'w') as fp:
    json.dump(winning_bids, fp)