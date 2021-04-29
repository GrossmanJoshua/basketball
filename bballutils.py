def pandas2md(df):
    out = []
    out.append('|'.join(df.columns))
    out.append('|'.join('----' for _ in df.columns))
    for _,i in df.iterrows():
        out.append('|'.join(str(j) for j in i.values))
    return '\n'.join(out)
