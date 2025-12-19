from typing import List
import logging
from app.models.models import Tweet
from app.services.twitter_api_client import TwitterAPIClient
from app.core.config import settings

logger = logging.getLogger(__name__)


class TwitterService:
    def __init__(self):
        self.api_client = TwitterAPIClient(bearer_token=settings.TWITTER_BEARER_TOKEN)

    async def get_tweets_by_hashtag(self, hashtag: str, limit: int = 10) -> List[Tweet]:
        # Validate limit (Twitter API accepts 10-100 for search)
        limit = max(10, min(limit, 100))
        
        logger.info(f"Fetching tweets for hashtag: {hashtag} (limit: {limit})")
        
        tweets_data = await self.api_client.search_tweets_by_hashtag(
            hashtag=hashtag, max_results=limit
        )
        
        tweets = [Tweet(**tweet) for tweet in tweets_data]
        logger.info(f"Retrieved {len(tweets)} tweets for #{hashtag}")
        
        return tweets

    async def get_user_tweets(self, username: str, limit: int = 10) -> List[Tweet]:
        # Validate limit (Twitter API requires 5-100)
        limit = max(5, min(limit, 100))
        
        logger.info(f"Fetching tweets for user: {username} (limit: {limit})")
        
        tweets_data = await self.api_client.get_user_tweets(
            username=username, max_results=limit
        )
        
        tweets = [Tweet(**tweet) for tweet in tweets_data]
        logger.info(f"Retrieved {len(tweets)} tweets for @{username}")
        
        return tweets

    async def close(self) -> None:
        await self.api_client.close()


# Singleton instance
twitter_service = TwitterService()