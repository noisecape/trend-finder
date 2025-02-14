# Reddit Virality Prediction & Trend Analysis 🚀

## 📌 Overview

This project aims to **predict the virality of Reddit posts**, analyse emerging trends, and extract meaningful insights from subreddit discussions. By leveraging **machine learning, embeddings, and retrieval-augmented generation (RAG)**, we can better understand **what makes a post go viral** and provide actionable insights for content creators, researchers, and businesses.

## 🎯 Current Achievements

Here’s what has been implemented so far:

✅ **Reddit Statistics & Metrics Extraction** – Using [`reddstats`](https://reddstats.com/) to pull key metrics from Reddit. ✅ **Large Language Model (LLM) Integration** – Using **LLaMA 3 (3B)** for text understanding and retrieval. ✅ **Embedding Generation & Storage** – Calculating embeddings for posts and storing them in a **vector database**. ✅ **Clustering & Visualization of Embeddings** – Implemented **PCA, t-SNE, and K-Means** to analyze post relationships in vector space. ✅ **Basic RAG System** – Given a query, retrieve the **most relevant subreddits** based on vector search.

## 🚀 Next Steps (Work in Progress)

Currently working on **scraping real Reddit data using Crawl4AI** to enrich our dataset with:

- **Real-world post engagement metrics** (Upvotes, comments, timestamps, etc.)
- **Trend analysis across subreddits**
- **Sentiment analysis** to classify opinions and emotions
- **Time-based virality tracking**
- **Training a classifier to identify whether a future post can go viral or not**

## 🔮 Future Roadmap

Here’s the vision for expanding this project:

1️⃣ **Feature Engineering** – Extract structured features from posts (length, sentiment, time of posting, etc.) 2️⃣ **Model Development** – Train ML models to predict a post’s virality. 3️⃣ **Interactive Dashboard** – Build a UI that visualizes subreddit trends and allows users to test virality predictions.

## 🤖 Tech Stack

- **Python** (Pandas, Scikit-Learn, PyTorch, Transformers, Datasets)
- **LLMs** (LLaMA 3, Hugging Face, Ollama)
- **Data Visualization** (Matplotlib, Seaborn, t-SNE, PCA)
- **Scraping** (Crawl4AI, Reddit API)

## 🔗 How to Get Started

1. Clone this repository:
   ```bash
   git clone https://github.com/noisecape/trend-finder.git
   cd trend-finder
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

## 📢 Contributions & Feedback

This is an evolving project, and contributions are welcome! Feel free to submit issues, pull requests, or ideas to improve the system. 🔥


