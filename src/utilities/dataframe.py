import pandas as pd

def merge_dataframes(dfs):
    """Takes a list of pandas dataframes and concatenates them"""

    new_dfs = pd.DataFrame()

    for df in dfs:
        new_dfs = pd.concat([new_dfs, df])

    new_dfs.reset_index(drop=True, inplace=True)
    return new_dfs