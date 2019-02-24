# todo: add code that checks to see if any bids are invalid

import pandas as pd
import numpy as np
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
                breakdown_string = f' ({row.Breakdown})' if isinstance(row.Breakdown, str) else ''
                f.write(f'{row.Player}, {row.Years} {year_string} at {row.AAV:{width}.{precision}}/year{breakdown_string}\n')
            f.write('\n')


def generate_all_bids_file(file_name, df, width=2, precision=4):
    with open(file_name, 'w') as f:
        for player in df.Player.unique():
            f.write(f'[b][u]{player}[/u][/b]\n')
            player_bids = df.loc[df['Player'] == player].sort_values(by=['AAV', 'Years', 'Y1', 'Order'], ascending=[False, False, False, True])
            for idx, row in player_bids.iterrows():
                year_string = 'year' if row.Years == 1 else 'years'
                breakdown_string = f' ({row.Breakdown})' if isinstance(row.Breakdown, str) else ''
                f.write(f'{row.Team}: {row.Years} {year_string} at {row.AAV:{width}.{precision}}/year{breakdown_string}\n')
            f.write('\n')


def generate_total_bids_json(df):
    bids = {}
    for player in df.Player.unique():
        player_df = df.loc[df['Player'] == player].drop(['Player', 'Order'], axis=1)
        player_df.set_index('Team', inplace=True)
        bids[player] = player_df.transpose().to_json()

    return bids


def generate_winning_bids_json(df):
    bids = {}
    for team in df.Team.unique():
        team_df = df.loc[df['Team'] == team].drop(['Team', 'Order'], axis=1)
        team_df.set_index('Player', inplace=True)
        bids[team] = team_df.transpose().to_json()

    return bids


def generate_player_bids_json(df):
    bids = {}
    for player in df.Player.unique():
        player_df = df.loc[df['Player'] == player].sort_values(by=['AAV', 'Years', 'Y1', 'Order'], ascending=[False, False, False, True]).drop(['Player', 'Order'], axis=1)
        player_df.set_index('Team', inplace=True)
        bids[player] = player_df.transpose().to_json()

    return bids


def write_json_file(file_name, val):
    with open(file_name, 'w') as fp:
        json.dump(val, fp)

df = pd.read_csv('bids.csv')

df['AAV'] = df['Total'] / df['Years']
for i in range(0, 5):
    val = ''
    try:
        df[f'Y{i+1}'] = pd.to_numeric(df['Breakdown'].str.split(",", n=1, expand=True)[i]).fillna(df['AAV'])
    except Exception as e:
        df[f'Y{i+1}'] = df['AAV']

df['Max'] = df[['Y1', 'Y2', 'Y3', 'Y4', 'Y5']].values.max(1)
df['Min'] = df[['Y1', 'Y2', 'Y3', 'Y4', 'Y5']].values.min(1)
df['MaxValid'] = df['AAV'] * 1.2 > df['Max']
df['MinValid'] = df['AAV'] * 0.8 < df['Min']
df['BaseValid'] = df['AAV'] > 0.4
df['Valid'] = df['MaxValid'] & df['MinValid'] & df['BaseValid']

generate_all_bids_file('all_players.txt', df)
all_bids = generate_total_bids_json(df)
all_players = generate_player_bids_json(df)

df = max_by_column(df, 'Player', 'AAV')
df = max_by_column(df, 'Player', 'Years')
df = max_by_column(df, 'Player', 'Y1')
df = min_by_column(df, 'Player', 'Order')
df.drop(['Y1', 'Y2', 'Y3', 'Y4', 'Y5', 'Max', 'Min'], axis=1, inplace=True)
# temp = df.Team.uniqu
winning_bids = generate_winning_bids_json(df)
write_json_file('all_bids.json', all_bids)
write_json_file('all_players.json', all_players)
write_json_file('winning_bids.json', winning_bids)
generate_winning_bids_file('winning_bids.txt', df)
