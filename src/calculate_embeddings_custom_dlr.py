import os
import re

import pandas as pd
import torch
from torch.utils.data import DataLoader, Dataset
from tqdm.auto import tqdm
from transformers import AutoModelForCausalLM, AutoTokenizer

# Change the current working directory to the script's directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

class CaptionDataset(Dataset):

        def __init__(self, tokenized_captions):
            super(CaptionDataset, self).__init__()
            self.tokenized_captions = tokenized_captions

        def __len__(self):
            return self.tokenized_captions['input_ids'].shape[0]

        def __getitem__(self, index):
            prompt = {key: tensor[index] for key, tensor in self.tokenized_captions.items()}
            return prompt, index


def process_data(prompts:[str]):
    # Remove list brackets and quotes
    cleaned_data = [re.sub(r"\s{2,}", " ", p.strip("[]'").replace("\\n", " ")) for p in prompts]

    return cleaned_data


def tokenize_data(prompts:[str], tokenizer):
    encodings = tokenizer(
        list(prompts),
        max_length=160,
        padding="max_length",
        truncation=True,
        return_tensors="pt"  # Directly return a PyTorch tensor
    )
    return encodings


def calculate_embeddings_hf_llama():
        
    model_id = 'meta-llama/Llama-3.2-3B-Instruct'
    df = pd.read_csv('./data/df_processed_all.csv')
    df.reset_index(drop=True, inplace=True)
    model = AutoModelForCausalLM.from_pretrained(model_id).to('cuda:0')
    tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-3.2-3B-Instruct", use_fast=True)
    tokenizer.pad_token = tokenizer.eos_token  # Use <eos> as padding token
    tokenizer.pad_token_id = tokenizer.eos_token_id

    processed_captions = process_data(df['prompt'].tolist())
    tokenized_captions = tokenize_data(processed_captions, tokenizer=tokenizer)
    prompt_dst = CaptionDataset(tokenized_captions=tokenized_captions)  
    model.eval()

    prompt_dlr = DataLoader(
        prompt_dst, 
        batch_size=64, 
        shuffle=False, 
        num_workers=5,
        pin_memory=True
    )

    eval_loop = tqdm(prompt_dlr, total=len(prompt_dlr))
    for data, idxs in eval_loop:
        data = {k: v.to('cuda:0') for k, v in data.items()}
        with torch.no_grad(), torch.autocast(device_type="cuda", dtype=torch.bfloat16):
            embs = model(**data, output_hidden_states=True)
            embeddings = embs.hidden_states[-1]  # Last hidden layer (batch_size, seq_len, hidden_dim)

            # Detach & move to CPU to avoid memory leaks
            embeddings = embeddings.detach().cpu()

        # Save each embedding into the DataFrame (you might want to post-process each embedding)
        # for i, emb in zip(idxs, embeddings):
        #     # For example, storing the full tensor as a NumPy array:
        #     df.at[i.item(), 'llama3.2_3b_instruct'] = emb.numpy()

    return df
 
if __name__ == "__main__":
    embeds_df = calculate_embeddings_hf_llama()
    print("All Done!")

