import enum
import json
import random
import time
from functools import partial
from typing import List

import pandas as pd
import praw
import yaml
from tqdm.auto import tqdm

random.seed(42)

import datetime

from src.data.validators import RedditComment, RedditPost

MAX_POSTS = 50
MIN_POSTS = 20
MIN_COMMENTS = 2
MAX_COMMENTS = 5
MAX_RETRIES = 5
MAX_DEPTH = 2


# Track API rate limits
def check_rate_limit(reddit, lower_bound:int=25):
    """Check Reddit API rate limits and wait if needed."""
    if hasattr(reddit, 'auth'):
        remaining = reddit.auth.limits.get('remaining', 1)
        reset_time = reddit.auth.limits.get('reset_timestamp', time.time())
        if remaining <= lower_bound:
            sleep_time = reset_time - time.time()
            if sleep_time > 0:
                print(f"⚠️ Rate limit hit! Sleeping for {sleep_time:.2f} seconds...")
                time.sleep(sleep_time)


# Function to fetch posts with rate limit handling
def fetch_data(subreddit_name, reddit_instance, weights:List[int]=[0.3, 0.3, 0.2, 0.2]):
    """Fetch posts from a subreddit with rate limit handling."""
    
    retries = 0
    posts = []
    comments = []

    while retries < MAX_RETRIES:
        try:
            subreddit = reddit_instance.subreddit(subreddit_name)
            n_posts = random.randint(MIN_POSTS, MAX_POSTS)
            controversil_w_filter = partial(subreddit.controversial, time_filter='year')
            top_w_filter = partial(subreddit.top, time_filter='year')
            post_kinds = [subreddit.hot, subreddit.new, controversil_w_filter, top_w_filter]
            
            for post in random.choices(post_kinds, weights=weights)[0](limit=n_posts):
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
                posts.append(reddit_post.__dict__)
                if post.num_comments > 0:
                    # Scraping comments for each post
                    more_comments = random.randint(MIN_COMMENTS, MAX_COMMENTS)
                    post.comments.replace_more(limit=more_comments)
                    for comment in post.comments.list(): # list() returns list of comments visited in BFS order
                        if comment.depth > MAX_DEPTH:
                            print("Max depth reached! Changing post!")
                            break
                        check_rate_limit(reddit_instance)
                        reddit_comment = RedditComment(
                            element_type = 'comment',
                            comment_id = comment.id,
                            parent_id = comment.parent_id if hasattr(comment, 'parent_id') else None,
                            subreddit_id = comment.subreddit_id,
                            author_premium = comment.author_premium if hasattr(comment, "author_fullname") else None,
                            created_utc = comment.created_utc,
                            score = comment.score,
                            gilded = comment.gilded,
                            body = comment.body,
                            edited = comment.edited,
                            depth = comment.depth,
                            controversiality=comment.controversiality,
                        )
                        comments.append(reddit_comment.__dict__)
            return posts, comments
        except Exception as e:
            if "RATELIMIT" in str(e) or "429" in str(e): # TODO: catch better the exception with proper handling.
                print(f"🚨 API Rate Limit hit! Checking Reddit's reset time...")
                check_rate_limit(reddit_instance)  # ✅ Instead of retrying blindly, use exact wait time
                retries += 1
            else:
                print(f"⚠️ API Exception: {e}")
                break  # Exit on non-rate-limit errors

    print("❌ Max retries reached. Skipping subreddit:", subreddit_name)
    return posts, comments  # Return whatever has been scraped

if __name__ == '__main__':

    # Load config for subreddits
    with open('./src/configs/subreddits.yaml') as f:
        subreddits = yaml.load(f, Loader=yaml.FullLoader)

    flattened_subreddits = [
        e for c in subreddits for sub_c in subreddits[c] for s in subreddits[c][sub_c] for e in subreddits[c][sub_c][s]
    ]

    # Load Reddit API credentials
    with open('./src/config.json') as f:
        config = json.load(f)

    reddit_instance = praw.Reddit(
        client_id=config['client_id'],
        client_secret=config['client_secret'],
        password=config['password'],
        user_agent=config['user_agent'],
        username=config['username']
    )


    assert reddit_instance.user.me() == config['username'], 'Reddit instance not authenticated!'

    subreddit_posts = []
    subreddit_comments = []
    # Scraping process
    subreddit_loop = tqdm(flattened_subreddits[:5], total=len(flattened_subreddits[5]))
    for subreddit_name in subreddit_loop:
        subreddit_loop.set_description(f"Scraping: {subreddit_name}")
        check_rate_limit(reddit_instance)

        # Fetch posts
        posts, comments = fetch_data(subreddit_name, reddit_instance)
        subreddit_posts.extend(posts)
        subreddit_comments.extend(comments)

    # Create pandas DataFrame
    posts_df = pd.DataFrame(subreddit_posts)
    comments_df = pd.DataFrame(subreddit_comments)
    timestamp = datetime.datetime.now().strftime("%d_%m_%Y_%H_%M_%S")
    posts_df.to_csv(f'./posts_{timestamp}.csv', index=False)
    comments_df.to_csv(f'./comments_{timestamp}.csv', index=False)
    print("✅ All done!")
