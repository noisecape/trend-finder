from pydantic import BaseModel, Field
from typing import Optional, Union

class RedditPost(BaseModel):
    element_type: str
    subreddit_id: str
    subreddit_display_name: str
    subreddit_subscribers: Optional[int] = None
    subreddit_type: Optional[str] = None
    subreddit_lang: Optional[str] = None
    subreddit_description: Optional[str] = None
    post_id: str
    title: str
    author: Optional[str] = None  # Handle deleted users
    created_utc: float
    selftext: str
    score: int
    num_comments: int
    url: str
    gilded: int
    num_crossposts: int
    over_18: bool
    permalink: str
    upvote_ratio: float

class RedditComment(BaseModel):
    """Optimized Pydantic model for tracking Reddit comment virality"""
    element_type:str
    comment_id: str
    parent_id: str  # Tracks comment hierarchy
    link_id: Optional[str] = None  # The Reddit post this comment belongs to
    subreddit: str
    author_fullname: Optional[str] = None
    author_premium: Optional[bool] = None
    created_utc: float  # Timestamp of comment
    score: int  # Total engagement score (upvotes - downvotes)
    ups: int  # Upvotes only
    downs: int  # Downvotes only
    num_reports: Optional[int]  # Reports (can indicate controversial topics)
    gilded: int  # If it received awards (signal for high-quality comments)
    body: str  # Actual comment text
    edited: Union[bool, float]  # True if edited, float if timestamped
    depth: int  # How deep this comment is in the conversation
    controversiality:int