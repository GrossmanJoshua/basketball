import os
import pandas as pd

THIS_DIR = os.path.abspath(os.path.dirname(__file__))

__all__ = [
    'player_data',
    'name_from_playerid',
    'playerids_from_lastname',
    'playerids_from_teamid'
]

# Load the players data from 
#
#  https://github.com/bttmly/nba
#
with open(os.path.join(THIS_DIR,'players.json')) as f:
    data_df = pd.read_json(f)

def player_data():
    '''Return the player data table'''
    return data_df

def name_from_playerid(playerid):
    '''Return a player name given their player ID'''
    row = data_df[data_df['playerId'] == playerid]
    if not len(row):
        return None
    else:
        row = row.iloc[0]
        return row['firstName'], row['lastName']

def playerids_from_lastname(lastname):
    '''Return a list of player IDs given a last name (partial match)'''
    rows = data_df[data_df['lastName'].str.contains(lastname)]
    if not len(rows):
        return None
    else:
        return [i for i in rows['playerId']]

def playerids_from_teamid(teamid):
    '''Return a list of player IDs given a team ID'''
    rows = data_df[data_df['teamId'] == teamid]
    if not len(rows):
        return None
    else:
        return [i for i in rows['playerId']]
  