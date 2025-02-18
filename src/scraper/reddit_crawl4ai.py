import asyncio
import json
import re
from typing import Any, Dict, List
import yaml
import pickle

import requests
from crawl4ai import (AsyncWebCrawler, BrowserConfig, CacheMode,
                      CrawlerMonitor, CrawlerRunConfig, DisplayMode,
                      RateLimiter)
from crawl4ai.async_dispatcher import MemoryAdaptiveDispatcher
from src.data.validators import RedditComment, RedditPost, Subreddit, RedditDataset

BASE_URL = "https://www.reddit.com"

rate_limiter = RateLimiter(
        base_delay=(2.0, 4.0),
        max_delay=30.0,
        max_retries=5,
        rate_limit_codes=[429, 503]
    )

monitor = CrawlerMonitor(
    max_visible_rows=10,
    display_mode=DisplayMode.DETAILED
)

dispatcher = MemoryAdaptiveDispatcher(
    memory_threshold_percent=90.0,
    check_interval=1.0,
    max_session_permit=10,
    rate_limiter=rate_limiter,
    monitor=monitor
)
browser_config = BrowserConfig(headless=True, verbose=False)
run_config = CrawlerRunConfig(
    cache_mode=CacheMode.BYPASS,
    stream=False
)

dispatcher = MemoryAdaptiveDispatcher(
    memory_threshold_percent=70.0,
    check_interval=1.0,
    max_session_permit=10,
    monitor=monitor,
)

async def crawl_batch(subreddits:dict, urls: List[str]) -> None:
    browser_config = BrowserConfig(headless=True, verbose=False)
    run_config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        stream=False
    )

    dispatcher = MemoryAdaptiveDispatcher(
        memory_threshold_percent=70.0,
        check_interval=1.0,
        max_session_permit=10,
        monitor=monitor,
    )

    async with AsyncWebCrawler(config=browser_config) as crawler:
        # Get all results at once
        results = await crawler.arun_many(
            urls=urls,
            config=run_config,
            dispatcher=dispatcher
        )
        validated_posts = []
        validated_comments = []
        # Process all results after completion
        for result in results:
            if result.success:
                # process result, extract relevant information from json payload
                print(f"Successfully crawled {result.url}")
                # Remove any unwanted characters (e.g., markdown artifacts like triple backticks)
                cleaned_content = re.sub(r'```[n]*', '', result.markdown).strip()

                # Attempt to load as JSON after cleaning
                try:
                    json_data = json.loads(cleaned_content)
                except json.JSONDecodeError as e:
                    print(f"Failed to load JSON from {result.url}: {e}")
                    continue

                # Extract relevant information from json payload
                # For example, extract post title and comments
                try:
                    validated_posts.append(RedditPost(**json_data[0]["data"]["children"][0]["data"]))
                    validated_comments.append([RedditComment(**comment["data"]) for comment in json_data[1]["data"]["children"]])

                except Exception as e:
                    print(f"Failed to validate data from {result.url}: {e}")
                    continue
            else:
                print(f"Failed to crawl {result.url}: {result.error_message}")
    
        return validated_posts, validated_comments


async def get_links_from_json_structure(subreddit_urls:str) -> List[str]:
    """Get URLs from Reddit r/news json structure"""
    # json_payload = "https://www.reddit.com/r/news/hot.json"
    # try:
    #     response = requests.get(json_payload)
    #     response.raise_for_status()
    #     data = response.json()
    #     urls = [f"{''.join([BASE_URL, post["data"]["permalink"]])}.json" for post in data["data"]["children"]]
    #     return urls
    # except requests.RequestException as e:
    #     print(f"Error: {e}")
    #     return []

    async with AsyncWebCrawler(config=browser_config) as crawler:
        # Get all results at once
        results = await crawler.arun_many(
            urls=subreddit_urls,
            config=run_config,
            dispatcher=dispatcher
        )

        urls = {}
        # Process all results after completion
        for result in results:
            if result.success:
                # process result, extract relevant information from json payload
                print(f"Successfully crawled {result.url}")
                # Remove any unwanted characters (e.g., markdown artifacts like triple backticks)
                cleaned_content = re.sub(r'```[n]*', '', result.markdown).strip()

                # Attempt to load as JSON after cleaning
                try:
                    json_data = json.loads(cleaned_content)
                except json.JSONDecodeError as e:
                    print(f"Failed to load JSON from {result.url}: {e}")
                    return []

                # Extract relevant information from json payload
                # For example, extract post title and comments
                try:
                    for post in json_data["data"]["children"]:
                        if post["data"]["subreddit"] in urls:
                            urls[post["data"]["subreddit"]].append(f"{''.join([BASE_URL, post["data"]["permalink"]])}.json")
                        else:
                            urls[post["data"]["subreddit"]] = [f"{''.join([BASE_URL, post["data"]["permalink"]])}.json"]
                except Exception as e:
                    print(f"Failed to validate data from {result.url}: {e}")
            else:
                print(f"Failed to crawl {result.url}: {result.error_message}")
                return []
        return urls
    

if __name__ == "__main__":
    base_url = "https://www.reddit.com/r/news/hot.json" #TODO: get it dynamically from the yaml file
    with open('./src/configs/subreddits.yaml') as file:
        categories = yaml.load(file, Loader=yaml.FullLoader)
    
    flattened_subreddits = []
    for c in categories:
        for sub_c in categories[c]:
            for s in categories[c][sub_c]:
                for e in categories[c][sub_c][s]:
                    url = f"{BASE_URL}/r/{e}/hot.json"
                    flattened_subreddits.append(url)
    
    subreddits = asyncio.run(get_links_from_json_structure(flattened_subreddits))
    flatten_post_urls = [url for urls in subreddits.values() for url in urls]
    validated_posts, validated_comments = asyncio.run(crawl_batch(subreddits, flatten_post_urls))
    print("Scraping completed")
    # save as pickle files
    with open('validated_posts.pkl', 'wb') as f:
        pickle.dump(validated_posts, f)
    with open('validated_comments.pkl', 'wb') as f:
        pickle.dump(validated_comments, f)
    print("Data saved as pickle files")