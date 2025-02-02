import os
import re

import numpy as np
import pandas as pd
import torch
from tqdm.auto import tqdm
from transformers import pipeline

from utilities.dataframe import format_prompts

# Change the current working directory to the script's directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

def calculate_embeddings(df, model_id):

    feature_extraction = pipeline(
        "feature-extraction",
        model=model_id,
        torch_dtype=torch.bfloat16,
        device_map="auto",
    )

    prompts = format_prompts(df['prompt'].tolist())
    df['prompt_processed'] = prompts
    df['llama3.2_3B_embs'] = None
    processing_loop = tqdm(enumerate(prompts), total=len(prompts))
    for idx, p in processing_loop:
        embs = feature_extraction(p)[0][-1]
        df.at[idx, 'llama3.2_3B_embs'] = embs
    return df


if __name__ == "__main__":
    model_id = 'meta-llama/Llama-3.2-3B-Instruct'
    df = pd.read_csv('./data/df_processed_all.csv')
    df.reset_index(drop=True, inplace=True)

    embeds_df = calculate_embeddings(df=df, model_id=model_id)

    embeds_df.to_csv('./data/df_processed_all_v2.csv', index=False)
    print("All Done!")

