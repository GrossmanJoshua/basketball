'''Default parameters used by many different destinations'''

REGULAR_SEASON = 'Regular Season'

PER_GAME = 'PerGame'

MEASURE_TYPE_ADVANCED = 'Advanced'

def SEASON(end_year):
    '''Get the season as needed by NBA stats for a season ending in year `end_year`.
    E.g. `SEASON(2018)` gives you `2017-181'''
    return '{}-{}'.format(int(end_year)-1, int(end_year) % 100)
