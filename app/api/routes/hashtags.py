from fastapi import APIRouter, Query, HTTPException
from typing import List
from app.models.models import Tweet
from app.services.twitter_service import twitter_service

router = APIRouter()


@router.get("/{hashtag}", response_model=List[Tweet])
async def get_tweets_by_hashtag(
    hashtag: str,
    limit: int = Query(default=30, ge=10, le=100, description="Number of tweets to retrieve")
):
    """
    Get tweets by hashtag.
    
    - **hashtag**: The hashtag to search for (without #) e.g., python
    - **limit**: Maximum number of tweets to retrieve (10-100, default: 30)
    """
    try:
        # Remove # if user included it
        clean_hashtag = hashtag.lstrip('#')
        
        tweets = await twitter_service.get_tweets_by_hashtag(clean_hashtag, limit)
        
        if not tweets:
            raise HTTPException(status_code=404, detail=f"No tweets found for #{clean_hashtag}")
        
        return tweets
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving tweets: {str(e)}")
