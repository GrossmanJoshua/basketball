import nbastats
import numpy as np
import pandas as pd

DIST_RANGE_VERY_TIGHT = '0-2 Feet - Very Tight'
DIST_RANGE_TIGHT = '2-4 Feet - Tight'
DIST_RANGE_OPEN = '4-6 Feet - Open'
DIST_RANGE_WIDE_OPEN = '6+ Feet - Wide Open'

REGULAR_SEASON = 'Regular Season'
PER_GAME = 'PerGame'

fields = {
 'CloseDefDistRange': '',
 'College': '',
 'Conference': '',
 'Country': '',
 'DateFrom': '',
 'DateTo': '',
 'Division': '',
 'DraftPick': '',
 'DraftYear': '',
 'DribbleRange': '',
 'GameScope': '',
 'GameSegment': '',
 'GeneralRange': '',
 'Height': '',
 'LastNGames': '0',
 'LeagueID': '00',
 'Location': '',
 'Month': '0',
 'OpponentTeamID': '0',
 'Outcome': '',
 'PORound': '0',
 'PaceAdjust': 'N',
 'PerMode': PER_GAME,
 'Period': '0',
 'PlayerExperience': '',
 'PlayerPosition': '',
 'PlusMinus': 'N',
 'Rank': 'N',
 'Season': '',
 'SeasonSegment': '',
 'SeasonType': REGULAR_SEASON,
 'ShotClockRange': '',
 'ShotDistRange': '',
 'StarterBench': '',
 'TeamID': '0',
 'TouchTimeRange': '',
 'VsConference': '',
 'VsDivision': '',
 'Weight': ''
}
    
def get_shottrack_data(**parms):
    '''Return the lineup data given the params'''
    global fields
    this_fields = dict(**fields)
    for i,j in parms.items():
        if i not in this_fields:
            raise ArgumentError("unknown parameter '{}'; see `shottrack.fields`".format(i))
        this_fields[i] = j
    js = nbastats._get_json('leaguedashteamptshot',this_fields,referer='lineups')
    df = nbastats._api_scrape(js)
    return df
