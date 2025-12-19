import httpx
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class TwitterAPIClient:
    BASE_URL = "https://api.twitter.com/2"

    def __init__(self, bearer_token: str):
        if not bearer_token:
            raise ValueError("Twitter Bearer Token is required")

        self.bearer_token = bearer_token
        self.client = httpx.AsyncClient(
            headers={
                "Authorization": f"Bearer {bearer_token}",
                "Content-Type": "application/json",
            },
            timeout=30.0,
        )

    async def search_tweets_by_hashtag(
        self, hashtag: str, max_results: int = 30
    ) -> List[Dict[str, Any]]:
        max_results = max(10, min(max_results, 100))
        
        # Clean hashtag
        clean_hashtag = hashtag.lstrip("#")

        # Build query parameters
        params = {
            "query": f"#{clean_hashtag} -is:retweet",
            "max_results": max_results,
            "tweet.fields": "created_at,public_metrics,entities,author_id,text",
            "expansions": "author_id",
            "user.fields": "name,username,id",
        }

        logger.info(f"Searching tweets for hashtag: #{clean_hashtag}")

        try:
            response = await self.client.get(
                f"{self.BASE_URL}/tweets/search/recent", params=params
            )
            response.raise_for_status()
            data = response.json()

            return self._transform_response(data)

        except httpx.HTTPStatusError as e:
            logger.error(f"Twitter API error: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Error searching tweets: {str(e)}")
            raise

    async def get_user_tweets(
        self, username: str, max_results: int = 30
    ) -> List[Dict[str, Any]]:
        max_results = max(5, min(max_results, 100))
        
        # Clean username
        clean_username = username.lstrip("@")

        logger.info(f"Getting tweets for user: @{clean_username}")

        try:
            # Step 1: Get user ID from username
            user_response = await self.client.get(
                f"{self.BASE_URL}/users/by/username/{clean_username}",
                params={"user.fields": "id,name,username"},
            )
            user_response.raise_for_status()
            user_data = user_response.json()

            if "data" not in user_data:
                raise ValueError(f"User @{clean_username} not found")

            user_id = user_data["data"]["id"]

            # Step 2: Get user's tweets
            params = {
                "max_results": max_results,
                "tweet.fields": "created_at,public_metrics,entities,text",
                "exclude": "retweets,replies",
            }

            tweets_response = await self.client.get(
                f"{self.BASE_URL}/users/{user_id}/tweets", params=params
            )
            tweets_response.raise_for_status()
            tweets_data = tweets_response.json()

            # Add user info to response for transformation
            if "includes" not in tweets_data:
                tweets_data["includes"] = {}
            tweets_data["includes"]["users"] = [user_data["data"]]

            # Add author_id to each tweet
            if "data" in tweets_data:
                for tweet in tweets_data["data"]:
                    tweet["author_id"] = user_id

            return self._transform_response(tweets_data)

        except httpx.HTTPStatusError as e:
            logger.error(f"Twitter API error: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Error getting user tweets: {str(e)}")
            raise

    def _transform_response(self, api_response: Dict[str, Any]) -> List[Dict[str, Any]]:
        tweets = []

        data = api_response.get("data", [])
        if not data:
            return tweets

        includes = api_response.get("includes", {})
        users = {user["id"]: user for user in includes.get("users", [])}

        for tweet in data:
            author = users.get(tweet.get("author_id"), {})

            # Extract hashtags from entities
            hashtags = []
            entities = tweet.get("entities", {})
            if "hashtags" in entities:
                hashtags = [f"#{tag['tag']}" for tag in entities["hashtags"]]

            # Get public metrics
            metrics = tweet.get("public_metrics", {})

            # Format date
            created_at = tweet.get("created_at", "")
            formatted_date = self._format_date(created_at)

            transformed = {
                "account": {
                    "fullname": author.get("name", "Unknown"),
                    "href": f"/{author.get('username', '')}",
                    "id": int(author.get("id", 0)),
                },
                "date": formatted_date,
                "hashtags": hashtags,
                "likes": metrics.get("like_count", 0),
                "replies": metrics.get("reply_count", 0),
                "retweets": metrics.get("retweet_count", 0),
                "text": tweet.get("text", ""),
            }
            tweets.append(transformed)

        return tweets

    def _format_date(self, iso_date: str) -> str:
        if not iso_date:
            return ""

        try:
            dt = datetime.fromisoformat(iso_date.replace("Z", "+00:00"))
            return dt.strftime("%I:%M %p - %d %b %Y")
        except Exception as e:
            logger.warning(f"Error formatting date {iso_date}: {e}")
            return iso_date

    async def close(self) -> None:
        await self.client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
