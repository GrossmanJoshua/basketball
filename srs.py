import numpy as np
import souploader
import pandas as pd

import numba

# See: https://www.pro-football-reference.com/blog/index4837.html?p=37

def load_games(season, months):
    df = None
    for month in months:
        url = 'https://www.basketball-reference.com/leagues/NBA_{season}_games-{month}.html'.format(
        season=season, month=month)
        soup = souploader.load_soup(url)
        table = souploader.soup_get_table_as_pandas(soup, id='schedule')
        
        table = table.rename(columns={
            'Visitor/Neutral': 'vis',
            'Home/Neutral': 'home',
            'PTS': 'vpts',
            'PTS.1': 'hpts',
        })
        
        if df is None:
            df = table
        else:
            df = pd.concat([df, table], axis=0, ignore_index=True)
    
    df.dropna(axis=0, how='any', subset=['vpts','hpts'], inplace=True)
    return df

@numba.njit
def srs_numba_(nteams, vpts, hpts, vidx, hidx):
    mov = np.zeros(nteams, dtype=np.int32)
    n_games_opp = np.zeros((nteams,nteams), dtype=np.int32)
    n_games = np.zeros(nteams, dtype=np.int32)
    N = len(vpts)
    for idx in range(N):
        vp,hp = vpts[idx],hpts[idx]
        if not np.isnan(vp) and not np.isnan(hp):
            vi,hi = vidx[idx],hidx[idx]
            n_games_opp[vi,hi] += 1
            n_games[vi] += 1
            n_games[hi] += 1
            mov[vi] += vp-hp
            mov[hi] += hp-vp
            
    N = len(n_games)
    mat = np.zeros((nteams,nteams))
    for idx in range(nteams):
        for j in range(nteams):
            ng = n_games_opp[idx,j] + n_games_opp[j,idx]
            if idx == j:
                mat[idx,j] = 1
            else:
                mat[idx,j] = -ng/n_games[idx]
    return mat, mov / n_games

def compute_srs(x):
    '''Compute the srs values in index order
    
    Returns:
        srs - array of srs ordered by hidx/vidx
    '''
    mat, mov = srs_numba_(
        len(x['vidx'].unique()),
        x['vpts'].values,
        x['hpts'].values,
        x['vidx'].values,
        x['hidx'].values)
    
    return np.linalg.lstsq(mat,mov,rcond=None)[0]

def get_srs(df):
    '''compute SRS from a dataframe of games
    
    Args:
        df - data frame with vis, home, vpts, hpts columns for
             visitor team, home team, visitor points and home points
             respectively. Each row is a game.
    '''
    teams = list(sorted(df.vis.unique()))
    tentry = {i:idx for idx,i in enumerate(teams)}
    
    x = df[['vis','home','vpts','hpts']].copy()
    x['vidx'] = x.apply(lambda i: tentry[i.vis], axis=1)
    x['hidx'] = x.apply(lambda i: tentry[i.home], axis=1)

    srs = compute_srs(x)
    
    srs_teams = {i: srs[j] for i,j in tentry.items()}
    srs_df = pd.DataFrame.from_dict(srs_teams, orient='index', columns=['srs'])
    srs_df.sort_values(by='srs',inplace=True,ascending=False)
    return srs_df

def split_team(df, team, games, new_team=None):
    '''Split a team into two teams
    
    Args:
        df - the data frame from `load_games`
        team - the team to split
        games - a list of games in order (this is 1-based, not 0-based)
                that the `team` played which will be renamed
                to a different team
        new_team - the new team name (default `team 2`)
        
    Example:
        if you want the 1st, 5th and 10th games played by the
        Boston Celtics to be treated as a separate team:
        
            split_team(df, 'Boston Celtics', [1,5,10], 'New Boston Celtics')
    '''
    
    if new_team is None:
        new_team = team + ' 2'
    
    df = df.copy()
    game_idx = df[(df['vis'] == team) | (df['home'] == team)].iloc[games-1].index

    df.loc[game_idx] = df.loc[game_idx].replace(team, new_team)
    return df