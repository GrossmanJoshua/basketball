import nbastats
import numpy as np
import pandas as pd

def get_lineup_data(parms):
    '''Return the lineup data given the params'''
    js = nbastats._get_json('leaguedashlineups',parms,referer='lineups')
    df = nbastats._api_scrape(js)
    return df

def split_lineup_to_columns(df, inplace=True):
    '''Splits the lineup groups into individual columns per player with a True/False
    if the player is in that lineup. These lineups are called "Has_<lineupid>"
    
    Also adds a LineupNumber column which is a unique integer for each lineup. Each
    player is assigned a single bit in the integer and all the players in that lineup
    have their bit positions ORd together.
    
    Returns:
      * the modified dataframe (which is modified in place if `inplace` is True).
      * The bit mapping table
    '''
    # Make a copy if not in place
    if not inplace:
        df = df.copy(deep=True)
        
    pl_ids = np.unique([int(j) for i in df['GROUP_ID'] for j in i.split(' - ')])

    bit_mapping = {i:idx for idx,i in enumerate(pl_ids)}

    x = [np.sum(2**np.array([bit_mapping[int(j)] for j in i.split(' - ')])) for i in df['GROUP_ID']]
    df['LineupNumber'] = pd.Series(x, index=df.index)

    x = [[int(j) for j in i.split(' - ')] for i in df['GROUP_ID']]
    for pid in pl_ids:
        df['Has_{}'.format(pid)] = pd.Series([pid in i for i in x], index=df.index)
        
    return df, bit_mapping


def get_player_onoff_data(df, field, bit_mapping):
    '''Takes a dataFrame loaded by `get_lineup_data`
    and post-processed with `split_lineup_to_column`
    and returns a new dataFrame with a row for lineup and
    player combination.
    
    The columns of the output dataFrame show how that lineup
    did in the column `field` when the player is on the
    court and how they fared in `field` when they were off
    the court (off court is a minute-weighted average of all
    the lineups where the 4 other players were the same). It
    also returns columns for minutes on and off.
    '''
    has_cols = [i for i in df.columns if i.startswith('Has_')]
    
    data = []
    
    for col in has_cols:
        # Remove the word 'Has_` from the column and that's the player id
        playerid = int(col[4:])
        
        # Get their `bit`
        player_bit = 1 << bit_mapping[playerid]
        player_bit

        # A boolean column saying whether a lineup has this player or not
        has_this_player = df[col]
        for lnum in df[has_this_player]['LineupNumber']:
            # Remove this player's `bit` from the lineup number
            # and then find all other lineups that have the
            # same 4 bits set (plus one other bit obviously)
            pnum = lnum & ~player_bit
            xdf = df[(~has_this_player) & 
                     ((df['LineupNumber'] & pnum) == pnum)]
            
            # If there are 0 total minutes for this lineup
            # without the player in question, then skip
            tmins = np.sum(xdf['MIN'])
            if tmins == 0:
                continue

            # Get the datat for this lineup when this player is on
            player_ondf = df[df['LineupNumber'] == lnum]
            on_rating = float(player_ondf[field])
            on_mins = float(player_ondf['MIN'])
            
            # Get the minutes-weighted average for the lineup when
            # the player is off
            avg_rating = np.sum(xdf['MIN'] * xdf[field]) / tmins

            data.append(dict(
                playerid=playerid,
                lineup=lnum,
                on_mins=on_mins,
                off_mins=tmins,
                on_rating=on_rating,
                off_rating=avg_rating,
            ))

    return pd.DataFrame(data, columns=data[0].keys())