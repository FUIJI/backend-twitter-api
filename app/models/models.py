from pydantic import BaseModel
from typing import List, Optional


class Account(BaseModel):
    fullname: str
    href: str
    id: int


class Tweet(BaseModel):
    account: Account
    date: str
    hashtags: List[str] = []
    likes: int = 0
    replies: int = 0
    retweets: int = 0
    text: str


class TweetsResponse(BaseModel):
    tweets: List[Tweet]
    count: int
    hashtag: Optional[str] = None
    username: Optional[str] = None
