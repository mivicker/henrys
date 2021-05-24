from pandas import DataFrame
from itertools import islice

def convert_excel_to_dataframe(wb, header = True, index = False):
    ws = wb.active
    data = ws.values

    if header and not index:
        cols = next(data)
        rows = list(data)
        
        return DataFrame(rows, columns=cols)

    return DataFrame(data)