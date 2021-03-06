from bs4 import BeautifulSoup
import pandas as pd
import os

def load_html(
    file,
    tableid,
    attrmatch=None,
    header_row=0,
    indexcol=None,
    get_headers=lambda cell: cell.text,
    title=None
):
    '''Load an HTML table from a file.
    
    file - the file to load
    tableid - the html `id` of the table
    attrmatch - match attributes in the rows to catch the rows you want to actually include
    header_row - the row to get from the header
    indexcol - a column to make the index of the table. Set to None to use pandas index
    get_headers - a function that converts a header row into a text string for the column name in pandas
    title - optionally set a title attribute
    '''
    # Read the file
    with open(file) as f:
        soup = BeautifulSoup(f)

    # Find the table
    table = soup.find('table',{'id':tableid})

    if not table:
        raise RuntimeError("couldn't find table `{}`".format(tableid))

    # Get a list of list from the columns
    table_cells = [
        [ j for j in i.find_all(['td','th']) ]
            for i in table.find_all('tr', attrs=attrmatch) #lambda row: row.tag == 'tr')
    ]

    if not table_cells:
        raise RuntimeError("no rows found")

    # Get the headers
    headers = [get_headers(i) for i in table_cells.pop(header_row)]
    
    # Convert to text
    vals = [[j.text for j in i] for i in table_cells]
    
    # Convert to a dataframe
    df = pd.DataFrame(vals,columns=headers)
    if indexcol is not None:
        df.set_index(indexcol,drop=True,inplace=True)
        df.index.name = None
    df.dropna(axis=0,how='any',inplace=True)

    # Convert to numeric
    for col in df.columns:
        try:
            tonum = pd.to_numeric(df[col])
            df[col] = tonum
        except (ValueError,TypeError):
            pass
    try:
        tonum = pd.to_numeric(df.index)
        df.index = tonum
    except ValueError:
        pass

    fname = os.path.splitext(os.path.basename(file))[0]
    setattr(df,'filename',file)
    if title is None:
        title = os.path.splitext(os.path.basename(file))[0]
    setattr(df,'title',title)
    return df