import json
import time
import pandas as pd
import praw
import yaml
from tqdm.auto import tqdm
from praw.exceptions import APIException, RedditAPIException

from src.data.validators import RedditComment, RedditPost

LIMIT_SUBREDDIT = 10
LIMIT_COMMENTS = 25
MAX_RETRIES = 5

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
    # reddit_instance.read_only = True

    assert reddit_instance.user.me() == config['username'], 'Reddit instance not authenticated!'

    # Track API rate limits
    def check_rate_limit(reddit):
        """Check Reddit API rate limits and wait if needed."""
        if hasattr(reddit, 'auth'):
            remaining = reddit.auth.limits.get('remaining', 1)
            reset_time = reddit.auth.limits.get('reset_timestamp', time.time())
            if remaining <= 0:
                sleep_time = reset_time - time.time()
                if sleep_time > 0:
                    print(f"⚠️ Rate limit hit! Sleeping for {sleep_time:.2f} seconds...")
                    time.sleep(sleep_time)

    # Function to fetch posts with rate limit handling
    def fetch_data(subreddit_name):
        """Fetch posts from a subreddit with rate limit handling."""

        retries = 0
        data = []

        while retries < MAX_RETRIES:
            try:
                subreddit = reddit_instance.subreddit(subreddit_name)
                for post in subreddit.hot(limit=LIMIT_SUBREDDIT):
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
                        for comment in post.comments.list(): # list() returns list of comments visited in BFS order
                            reddit_comment = RedditComment(
                                element_type = 'comment',
                                comment_id = comment.id,
                                author_full_name = comment.author_fullname if hasattr(comment, "author_fullname") else None,
                                author_premium = comment.author_premium if hasattr(comment, "author_fullname") else None,
                                created_utc = comment.created_utc,
                                subreddit_id = comment.subreddit_id,
                                num_reports=comment.num_reports,
                                score = comment.score,
                                gilded = comment.gilded,
                                body = comment.body,
                                edited = comment.edited,
                                permalink = comment.permalink,
                                depth = comment.depth,
                                controversiality=comment.controversiality,
                                parent_id = comment.parent_id if hasattr(comment, 'parent_id') else None
                            )
                            data.append(reddit_comment.__dict__)
                return data
            except Exception as e:
                if "RATELIMIT" in str(e) or "429" in str(e): # TODO: catch better the exception with proper handling.
                    print(f"🚨 API Rate Limit hit! Checking Reddit's reset time...")
                    check_rate_limit(reddit_instance)  # ✅ Instead of retrying blindly, use exact wait time
                    retries += 1
                else:
                    print(f"⚠️ API Exception: {e}")
                    break  # Exit on non-rate-limit errors

        print("❌ Max retries reached. Skipping subreddit:", subreddit_name)
        return data  # Return whatever has been scraped


    subreddit_data = []
    # Scraping process
    subreddit_loop = tqdm(flattened_subreddits, total=len(flattened_subreddits))
    
    for subreddit_name in subreddit_loop:
        subreddit_loop.set_description(f"Scraping: {subreddit_name}")
        check_rate_limit(reddit_instance)

        # Fetch posts
        data = fetch_data(subreddit_name)
        subreddit_data.extend(data)

    # Create pandas DataFrame
    subreddit_df = pd.DataFrame(data)
    subreddit_df.to_csv('./data.csv', index=False)
    print("✅ All done!")
