from fastapi import APIRouter, Query, HTTPException
from typing import List
from app.models.models import Tweet
from app.services.twitter_service import twitter_service

router = APIRouter()


@router.get("/{username}", response_model=List[Tweet])
async def get_user_tweets(
    username: str,
    limit: int = Query(default=10, ge=5, le=100, description="Number of tweets (5-100)")
):
    """
    Get tweets from a user's timeline.
    
    - **username**: Twitter username (without @) e.g., elonmusk
    - **limit**: Maximum number of tweets (5-100, default: 10)
    """
    try:
        # Remove @ if user included it
        clean_username = username.lstrip('@')
        
        tweets = await twitter_service.get_user_tweets(clean_username, limit)
        
        if not tweets:
            raise HTTPException(status_code=404, detail=f"No tweets found for @{clean_username}")
        
        return tweets
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving tweets: {str(e)}")