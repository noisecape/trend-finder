from datasets import load_dataset

# Login using e.g. `huggingface-cli login` to access this dataset
start=375
stop=375
range_to_iterate = range(start, stop+1)
for r in range_to_iterate:
    print(f"Download-Loading {r}")
    df = load_dataset(f"gk4u/reddit_dataset_104", data_files=f"data/train-DataEntity_chunk_{r}.parquet")['train'].to_pandas()
    print(f"Download-Loaded {r}")