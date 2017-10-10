team_color = {
'ATL':'E03A3E',
'BOS':'008348',
'BRK':'Black',
'CHI':'CE1141',
'CHO':'008CA8',
'CLE':'860038',
'DAL':'0053BC',
'DEN':'4FA8FF',
'DET':'006BB6',
'GSW':'FDB927',
'HOU':'CE1141',
'IND':'FFC633',
'LAC':'ED174C',
'LAL':'552582',
'MEM':'23375B',
'MIA':'98002E',
'MIL':'00471B',
'MIN':'002B5C',
'NOP':'B4975A',
'NYK':'F58426',
'OKC':'007DC3',
'ORL':'007DC5',
'PHI':'006BB6',
'PHO':'E56020',
'POR':'C8102E',
'SAC':'724C9F',
'SAS':'B6BFBF',
'TOR':'CE1141',
'UTA':'00471B',
'WAS':'F5002F'
}

import htmltable

def load_bbref(file, tableid, indexcol='Rk', **kwargs):
    def get_headers(row):
        if not row.text.strip():
            return row['data-stat']
        else:
            return row.text

    return htmltable.load_html(
        file,
        tableid,
        attrmatch={'class': lambda cls: not (cls and cls=='thead')},
        header_row=0, get_headers=get_headers,
        indexcol=indexcol,
        **kwargs
    )
