import nbastats
import numpy as np
import pandas as pd
from .parameters import *

DIST_RANGE_VERY_TIGHT = '0-2 Feet - Very Tight'
DIST_RANGE_TIGHT = '2-4 Feet - Tight'
DIST_RANGE_OPEN = '4-6 Feet - Open'
DIST_RANGE_WIDE_OPEN = '6+ Feet - Wide Open'

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
    '''Return the shot-tracking data given the params'''
    global fields
    this_fields = nbastats._merge_fields(fields, parms)
    js = nbastats._get_json('leaguedashteamptshot',this_fields,referer='lineups')
    df = nbastats._api_scrape(js)
    return df
