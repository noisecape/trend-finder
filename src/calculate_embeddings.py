from langchain_ollama.embeddings import OllamaEmbeddings
import numpy as np
import pandas as pd
import os
from tqdm.auto import tqdm

# Change the current working directory to the script's directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

class EmbeddingTemplate:

    def __init__(
            self, 
            short_description:str, 
            subreddit_name:str, 
            subscribers:str, 
            created_date:str,
            ranking:str,
            growth_day:str,
            growth_week:str,
            growth_month:str,
            growth_absolute_day:str,
            growth_absolute_week:str,
            growth_absolute_month:str,
            ):

        self.prompt = f"""
        <|start|>Information about subreddit:
        <|short description|>{short_description if short_description else 'None'}
        <|subreddit_name|>{subreddit_name if subreddit_name else 'None'}
        <|subscribers|>{subscribers if subscribers else 'None'}
        <|created_date|>{created_date if created_date else 'None'}
        <|ranking|>{ranking if ranking else 'None'}
        <|growth_day|>{growth_day if growth_day else 'None'}
        <|growth_week|>{growth_week if growth_week else 'None'}
        <|growth_month|>{growth_month if growth_month else 'None'}
        <|growth_absolute_day|>{growth_absolute_day if growth_absolute_day else 'None'}
        <|growth_absolute_week|>{growth_absolute_week if growth_absolute_week else 'None'}
        <|growth_absolute_month|>{growth_absolute_month if growth_absolute_month else 'None'}
        <|end|>"""

def calculate_embeddings(df:pd.DataFrame):
    """calculate the embeddings using lanchain-ollama"""

    embed_model = OllamaEmbeddings(model='llama3.2:3b')

    processing_loop = tqdm(df.iterrows(), total=len(df))
    for idx, row in processing_loop:

        short_description = row['description']
        subreddit_name = row['subredditName']
        subscribers = row['subscribers']
        created_date = row['createdDate']
        ranking = row['ranking']
        growth_day = row['growthDay']
        growth_week = row['growthWeek']
        growth_month = row['growthMonth']
        absolute_growth_day = row['growthAbsoluteDay']
        absolute_growth_week = row['growthAbsoluteWeek']
        absolute_growth_month = row['growthAbsoluteMonth']

        embedding_template = EmbeddingTemplate(
            short_description=short_description,
            subreddit_name=subreddit_name,
            subscribers=subscribers,
            created_date=created_date,
            ranking=ranking,
            growth_day=growth_day,
            growth_week=growth_week,
            growth_month=growth_month,
            growth_absolute_day=absolute_growth_day,
            growth_absolute_week=absolute_growth_week,
            growth_absolute_month=absolute_growth_month
        )

        df.loc[idx, 'prompt'] = [embedding_template.prompt]
        df.loc[idx, 'embs'] = str(embed_model.embed_query(embedding_template.prompt))

    return df
 
if __name__ == "__main__":
    df = pd.read_csv("./data/results_50001_100000.csv")
    df.reset_index(drop=True, inplace=True)
    embeds_df = calculate_embeddings(df)
