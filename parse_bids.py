# todo: add code that checks to see if any bids are invalid

import pandas as pd
import json


def max_by_column(df, groupby_name, max_name, sort=False):
    idx = df.groupby([groupby_name], sort=sort)[max_name].transform(max) == df[max_name]
    return df[idx]


def min_by_column(df, groupby_name, min_name, sort=False):
    idx = df.groupby([groupby_name], sort=sort)[min_name].transform(min) == df[min_name]
    return df[idx]


def generate_winning_bids_file(file_name, df, width=2, precision=4):
    with open(file_name, 'w') as f:
        for team in df.Team.unique():
            f.write(f'[b][u]{team}[/u][/b]\n')
            winning_df = df.loc[df['Team'] == team]
            for idx, row in winning_df.iterrows():
                year_string = 'year' if row.Years == 1 else 'years'
                f.write(f'{row.Player}, {row.Years} {year_string} at {row.AAV:{width}.{precision}}/year\n')
            winning_df.set_index('Player', inplace=True)
            f.write('\n')


def generate_total_bids_json(file_name, df):
    winning_bids = {}
    for player in df.Player.unique():
        winning_df = df.loc[df['Player'] == player].drop(['Player', 'Order'], axis=1)
    winning_df.set_index('Team', inplace=True)
    winning_bids[player] = winning_df.transpose().to_json()

    with open(file_name, 'w') as fp:
        json.dump(winning_bids, fp)


df = pd.read_csv('bids.csv')

df['AAV'] = df['Total'] / df['Years']
df['Y1'] = pd.to_numeric(df['Breakdown'].str.split(",", n=1, expand=True)[0]).fillna(df['AAV'])

teams = df['Team'].unique()
players = df['Player'].unique()

df = max_by_column(df, 'Player', 'AAV')
df = max_by_column(df, 'Player', 'Years')
df = max_by_column(df, 'Player', 'Y1')
df = min_by_column(df, 'Player', 'Order')
df.drop('Y1', axis=1, inplace=True)

generate_winning_bids_file('winning_bids.txt', df)

generate_total_bids_json('all_bids.json', df)
