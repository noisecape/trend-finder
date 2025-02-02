import pandas as pd
import re

def merge_dataframes(dfs):
    """Takes a list of pandas dataframes and concatenates them"""

    new_dfs = pd.DataFrame()

    for df in dfs:
        new_dfs = pd.concat([new_dfs, df])

    new_dfs.reset_index(drop=True, inplace=True)
    return new_dfs

def format_prompts(prompts:[str]):
    # Remove list brackets and quotes
    cleaned_data = [re.sub(r"\s{2,}", " ", p.strip("[]'").replace("\\n", " ")) for p in prompts]

    return cleaned_data