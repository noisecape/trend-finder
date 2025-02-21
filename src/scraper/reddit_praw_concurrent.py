import concurrent.futures
import json
import threading
import time

import pandas as pd
import praw
import yaml
from tqdm.auto import tqdm

from src.data.validators import RedditComment, RedditPost

# Constants
LIMIT_SUBREDDIT = 50
LIMIT_COMMENTS = 25
MAX_RETRIES = 5

rate_limit_lock = threading.Lock()

# Load config for subreddits
with open('./src/configs/subreddits.yaml') as f:
    subreddits = yaml.load(f, Loader=yaml.FullLoader)

flattened_subreddits = [
    e for c in subreddits for sub_c in subreddits[c]
    for s in subreddits[c][sub_c] for e in subreddits[c][sub_c][s]
]

# Load Reddit API credentials
with open('./src/config.json') as f:
    config = json.load(f)

def check_rate_limit(reddit, lower_bound: int = 25):
    """Check Reddit API rate limits and wait if needed, using a global lock."""
    with rate_limit_lock:
        if hasattr(reddit, 'auth'):
            remaining = reddit.auth.limits.get('remaining', 1)
            reset_time = reddit.auth.limits.get('reset_timestamp', time.time())
            if remaining <= lower_bound:
                sleep_time = reset_time - time.time()
                if sleep_time > 0:
                    print(f"⚠️ Rate limit hit! Sleeping for {sleep_time:.2f} seconds...")
                    time.sleep(sleep_time)

def fetch_data(reddit_instance, subreddit_name):
    """Fetch posts and comments from a subreddit with rate limit handling."""
    retries = 0
    data = []

    while retries < MAX_RETRIES:
        try:
            subreddit = reddit_instance.subreddit(subreddit_name)
            for post in subreddit.hot(limit=LIMIT_SUBREDDIT):
                check_rate_limit(reddit_instance)
                reddit_post = RedditPost(
                    element_type="post",
                    subreddit_id=post.subreddit.id,
                    subreddit_display_name=post.subreddit.display_name,
                    post_id=post.id,
                    title=post.title,
                    author=post.author_fullname if hasattr(post, "author_fullname") else None,
                    created_utc=post.created_utc,
                    selftext=post.selftext,
                    score=post.score,
                    num_comments=post.num_comments,
                    url=post.url,
                    gilded=post.gilded,
                    num_crossposts=post.num_crossposts,
                    over_18=post.over_18,
                    permalink=post.permalink,
                    upvote_ratio=post.upvote_ratio
                )
                data.append(reddit_post.__dict__)
                if post.num_comments > 0:
                    # Scraping comments for each post
                    post.comments.replace_more(limit=LIMIT_COMMENTS)
                    for comment in post.comments.list():
                        check_rate_limit(reddit_instance)
                        reddit_comment = RedditComment(
                            element_type='comment',
                            comment_id=comment.id,
                            author_full_name=comment.author_fullname if hasattr(comment, "author_fullname") else None,
                            author_premium=comment.author_premium if hasattr(comment, "author_fullname") else None,
                            created_utc=comment.created_utc,
                            subreddit_id=comment.subreddit_id,
                            num_reports=comment.num_reports,
                            score=comment.score,
                            gilded=comment.gilded,
                            body=comment.body,
                            edited=comment.edited,
                            permalink=comment.permalink,
                            depth=comment.depth,
                            controversiality=comment.controversiality,
                            parent_id=comment.parent_id if hasattr(comment, 'parent_id') else None
                        )
                        data.append(reddit_comment.__dict__)
            return data
        except Exception as e:
            if "RATELIMIT" in str(e) or "429" in str(e):
                print(f"🚨 API Rate Limit hit on {subreddit_name}! Checking reset time...")
                check_rate_limit(reddit_instance)
                retries += 1
            else:
                print(f"⚠️ API Exception on {subreddit_name}: {e}")
                break

    print("❌ Max retries reached. Skipping subreddit:", subreddit_name)
    return data

def fetch_data_for_subreddit(subreddit_name, config):
    """Creates a local Reddit instance and fetches data for a given subreddit."""
    reddit_instance = praw.Reddit(
        client_id=config['client_id'],
        client_secret=config['client_secret'],
        password=config['password'],
        user_agent=config['user_agent'],
        username=config['username']
    )
    # Optional authentication check:
    assert reddit_instance.user.me() == config['username'], 'Reddit instance not authenticated!'
    return fetch_data(reddit_instance, subreddit_name)

def main():
    subreddit_data = []

    # Use ThreadPoolExecutor to run requests concurrently
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        # Submit tasks for each subreddit
        future_to_sub = {
            executor.submit(fetch_data_for_subreddit, sub, config): sub
            for sub in flattened_subreddits
        }

        # Use tqdm to show progress
        for future in tqdm(concurrent.futures.as_completed(future_to_sub),
                           total=len(future_to_sub),
                           desc="Scraping subreddits"):
            try:
                result = future.result()
                subreddit_data.extend(result)
            except Exception as exc:
                print(f"Subreddit {future_to_sub[future]} generated an exception: {exc}")

    # Create pandas DataFrame and save to CSV
    subreddit_df = pd.DataFrame(subreddit_data)
    subreddit_df.to_csv('./data.csv', index=False)
    print("✅ All done!")

if __name__ == '__main__':
    main()