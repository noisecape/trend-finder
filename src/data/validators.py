from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Union

class RedditPost(BaseModel):
    """Pydantic model for a Reddit post"""
    subreddit_id: str
    approved_at_utc: Optional[object] = None
    subreddit: str
    selftext: str
    user_reports: List[object] = []
    saved: bool
    mod_reason_title: Optional[object] = None
    gilded: int
    clicked: bool
    title: str
    link_flair_richtext: List[object] = []
    subreddit_name_prefixed: str
    hidden: bool
    pwls: int
    link_flair_css_class: Optional[object] = None
    downs: int
    top_awarded_type: Optional[object] = None
    hide_score: bool
    name: str
    quarantine: bool
    link_flair_text_color: str
    upvote_ratio: float
    author_flair_background_color: Optional[object] = None
    subreddit_type: str
    ups: int
    total_awards_received: int
    media_embed: Dict[str, object] = {}
    author_flair_template_id: Optional[object] = None
    is_original_content: bool
    author_fullname: str
    secure_media: Optional[object] = None
    is_reddit_media_domain: bool
    is_meta: bool
    category: Optional[object] = None
    secure_media_embed: Dict[str, object] = {}
    link_flair_text: Optional[object] = None
    can_mod_post: bool
    score: int
    approved_by: Optional[object] = None
    is_created_from_ads_ui: bool
    author_premium: bool
    thumbnail: str
    edited: bool
    author_flair_css_class: Optional[object] = None
    author_flair_richtext: List[object] = []
    gildings: Dict[str, object] = {}
    content_categories: Optional[object] = None
    is_self: bool
    mod_note: Optional[object] = None
    created: float
    link_flair_type: str
    wls: int
    removed_by_category: Optional[object] = None
    banned_by: Optional[object] = None
    author_flair_type: str
    domain: str
    allow_live_comments: bool
    selftext_html: Optional[object] = None
    likes: Optional[object] = None
    suggested_sort: Optional[object] = None
    banned_at_utc: Optional[object] = None
    url_overridden_by_dest: str
    view_count: Optional[object] = None
    archived: bool
    no_follow: bool
    is_crosspostable: bool
    pinned: bool
    over_18: bool
    all_awardings: List[object] = []
    awarders: List[object] = []
    media_only: bool
    can_gild: bool
    spoiler: bool
    locked: bool
    author_flair_text: Optional[object] = None
    treatment_tags: List[object] = []
    visited: bool
    removed_by: Optional[object] = None
    num_reports: Optional[object] = None
    distinguished: Optional[object] = None
    author_is_blocked: bool
    mod_reason_by: Optional[object] = None
    removal_reason: Optional[object] = None
    link_flair_background_color: str
    id: str
    is_robot_indexable: bool
    num_duplicates: int
    report_reasons: Optional[object] = None
    author: str
    discussion_type: Optional[object] = None
    num_comments: int
    send_replies: bool
    media: Optional[object] = None
    contest_mode: bool
    author_patreon_flair: bool
    author_flair_text_color: Optional[object] = None
    permalink: str
    stickied: bool
    url: str
    subreddit_subscribers: int
    created_utc: float
    num_crossposts: int
    mod_reports: List[object] = []
    is_video: bool

class RedditReplies(BaseModel):
    """Represents nested replies in Reddit comments"""
    kind: str
    data: Dict[str, object]  # This holds nested "Listing" data

    # process nested replies
    def process_replies(self) -> List["RedditComment"]:
        """Process nested replies"""
        replies = self.data["children"]
        return [RedditComment(**reply["data"]) for reply in replies]

class RedditComment(BaseModel):
    """Pydantic model for a Reddit comment"""
    subreddit_id: str
    approved_at_utc: Optional[object] = None
    author_is_blocked: bool
    comment_type: Optional[object] = None
    awarders: List[str] = []
    mod_reason_by: Optional[object] = None
    banned_by: Optional[object] = None
    author_flair_type: str
    total_awards_received: int
    subreddit: str
    author_flair_template_id: Optional[object] = None
    likes: Optional[object] = None
    replies: Optional[Union[RedditReplies, str]] = None  # Handles nested reply structures
    user_reports: List[object] = []
    saved: bool
    id: str
    banned_at_utc: Optional[object] = None
    mod_reason_title: Optional[object] = None
    gilded: int
    archived: bool
    collapsed_reason_code: Optional[object] = None
    no_follow: bool
    author: str
    can_mod_post: bool
    created_utc: float
    send_replies: bool
    parent_id: str
    score: int
    author_fullname: str
    approved_by: Optional[object] = None
    mod_note: Optional[object] = None
    all_awardings: List[object] = []
    collapsed: bool
    body: str
    edited: Union[bool, float]
    top_awarded_type: Optional[object] = None
    author_flair_css_class: Optional[object] = None
    name: str
    is_submitter: bool
    downs: int
    author_flair_richtext: List[object] = []
    author_patreon_flair: bool
    body_html: str
    removal_reason: Optional[object] = None
    collapsed_reason: Optional[object] = None
    distinguished: Optional[object] = None
    associated_award: Optional[object] = None
    stickied: bool
    author_premium: bool
    can_gild: bool
    gildings: Dict[str, object] = {}
    unrepliable_reason: Optional[object] = None
    author_flair_text_color: Optional[object] = None
    score_hidden: bool
    permalink: str
    subreddit_type: str
    locked: bool
    report_reasons: Optional[object] = None
    created: float
    author_flair_text: Optional[object] = None
    treatment_tags: List[object] = []
    link_id: str
    subreddit_name_prefixed: str
    controversiality: int
    depth: int
    author_flair_background_color: Optional[object] = None
    collapsed_because_crowd_control: Optional[object] = None
    mod_reports: List[object] = []
    num_reports: Optional[object] = None
    ups: int

class Subreddit(BaseModel):
    """Pydantic model for a subreddit"""
    title: str
    url:str
    posts: List[RedditPost]
    comments: List[List[RedditComment]]
    num_posts: int
    num_comments: int


class RedditDataset(BaseModel):
    """Pydantic model for a dataset"""
    subreddit: List[Subreddit]
    url: str
    num_posts: int
    num_comments: int
    num_comments_scraped: int

