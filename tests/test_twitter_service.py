import pytest

from unittest.mock import AsyncMock, patch, MagicMock
from app.services.twitter_service import TwitterService


@pytest.fixture
def mock_api_client():
    with patch('app.services.twitter_service.TwitterAPIClient') as mock:
        client = mock.return_value
        client.search_tweets_by_hashtag = AsyncMock()
        client.get_user_tweets = AsyncMock()
        client.close = AsyncMock()
        yield client


@pytest.fixture
def mock_tweet_model():
    with patch('app.services.twitter_service.Tweet') as mock:
        mock.side_effect = lambda **kwargs: MagicMock(**kwargs)
        yield mock


# ==================== Hashtag Search Tests ====================

@pytest.mark.asyncio
async def test_get_tweets_by_hashtag_default_limit(mock_api_client, mock_tweet_model):
    """Test searching tweets by hashtag with default limit (10)"""
    mock_api_client.search_tweets_by_hashtag.return_value = [
        {"text": "Learning #python is fun!", "likes": 10}
    ]
    
    service = TwitterService()
    tweets = await service.get_tweets_by_hashtag("python")
    
    # Should use minimum 10 for search endpoint
    mock_api_client.search_tweets_by_hashtag.assert_awaited_once_with(
        hashtag="python", max_results=10
    )
    assert len(tweets) == 1


@pytest.mark.asyncio
async def test_get_tweets_by_hashtag_custom_limit(mock_api_client, mock_tweet_model):
    """Test searching tweets with custom limit"""
    mock_api_client.search_tweets_by_hashtag.return_value = [
        {"text": f"Tweet {i}", "likes": i} for i in range(20)
    ]
    
    service = TwitterService()
    tweets = await service.get_tweets_by_hashtag("python", limit=20)
    
    mock_api_client.search_tweets_by_hashtag.assert_awaited_once_with(
        hashtag="python", max_results=20
    )
    assert len(tweets) == 20


@pytest.mark.asyncio
async def test_get_tweets_by_hashtag_below_minimum(mock_api_client, mock_tweet_model):
    """Test that limit below 10 is adjusted to 10"""
    mock_api_client.search_tweets_by_hashtag.return_value = []
    
    service = TwitterService()
    await service.get_tweets_by_hashtag("python", limit=5)
    
    # Should auto-adjust to 10
    mock_api_client.search_tweets_by_hashtag.assert_awaited_once_with(
        hashtag="python", max_results=10
    )


@pytest.mark.asyncio
async def test_get_tweets_by_hashtag_with_hash_symbol(mock_api_client, mock_tweet_model):
    """Test hashtag search with # prefix"""
    mock_api_client.search_tweets_by_hashtag.return_value = [
        {"text": "Hello #python", "likes": 5}
    ]
    
    service = TwitterService()
    tweets = await service.get_tweets_by_hashtag("#python")
    
    # Should pass hashtag without # to API client
    mock_api_client.search_tweets_by_hashtag.assert_awaited_once_with(
        hashtag="#python", max_results=10
    )
    assert len(tweets) == 1


@pytest.mark.asyncio
async def test_get_tweets_by_hashtag_empty_result(mock_api_client, mock_tweet_model):
    """Test hashtag search with no results"""
    mock_api_client.search_tweets_by_hashtag.return_value = []
    
    service = TwitterService()
    tweets = await service.get_tweets_by_hashtag("veryrarehashtag123")
    
    assert len(tweets) == 0


# ==================== User Tweets Tests ====================

@pytest.mark.asyncio
async def test_get_user_tweets_default_limit(mock_api_client, mock_tweet_model):
    """Test getting user tweets with default limit (10)"""
    mock_api_client.get_user_tweets.return_value = [
        {"text": "My tweet", "likes": 5}
    ]
    
    service = TwitterService()
    tweets = await service.get_user_tweets("alice")
    
    mock_api_client.get_user_tweets.assert_awaited_once_with(
        username="alice", max_results=10
    )
    assert len(tweets) == 1


@pytest.mark.asyncio
async def test_get_user_tweets_custom_limit(mock_api_client, mock_tweet_model):
    """Test getting user tweets with custom limit"""
    mock_api_client.get_user_tweets.return_value = [
        {"text": f"Tweet {i}", "likes": i} for i in range(15)
    ]
    
    service = TwitterService()
    tweets = await service.get_user_tweets("bob", limit=15)
    
    mock_api_client.get_user_tweets.assert_awaited_once_with(
        username="bob", max_results=15
    )
    assert len(tweets) == 15


@pytest.mark.asyncio
async def test_get_user_tweets_below_minimum(mock_api_client, mock_tweet_model):
    """Test that limit below 5 is adjusted to 5 for user tweets"""
    mock_api_client.get_user_tweets.return_value = []
    
    service = TwitterService()
    await service.get_user_tweets("bob", limit=1)
    
    # Should auto-adjust to 5 (user endpoint allows 5)
    mock_api_client.get_user_tweets.assert_awaited_once_with(
        username="bob", max_results=5
    )


@pytest.mark.asyncio
async def test_get_user_tweets_with_at_symbol(mock_api_client, mock_tweet_model):
    """Test user tweets with @ prefix"""
    mock_api_client.get_user_tweets.return_value = [
        {"text": "Hello world", "likes": 10}
    ]
    
    service = TwitterService()
    tweets = await service.get_user_tweets("@elonmusk", limit=10)
    
    # Should pass username with @ to API client (client will clean it)
    mock_api_client.get_user_tweets.assert_awaited_once_with(
        username="@elonmusk", max_results=10
    )
    assert len(tweets) == 1


@pytest.mark.asyncio
async def test_get_user_tweets_empty_result(mock_api_client, mock_tweet_model):
    """Test user tweets with no results"""
    mock_api_client.get_user_tweets.return_value = []
    
    service = TwitterService()
    tweets = await service.get_user_tweets("nonexistentuser123")
    
    assert len(tweets) == 0


# ==================== Resource Management Tests ====================

@pytest.mark.asyncio
async def test_close(mock_api_client):
    """Test proper cleanup of API client resources"""
    service = TwitterService()
    await service.close()
    
    mock_api_client.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_multiple_operations_same_service(mock_api_client, mock_tweet_model):
    """Test multiple operations on the same service instance"""
    mock_api_client.search_tweets_by_hashtag.return_value = [
        {"text": "Tweet 1", "likes": 1}
    ]
    mock_api_client.get_user_tweets.return_value = [
        {"text": "Tweet 2", "likes": 2}
    ]
    
    service = TwitterService()
    
    # First operation
    tweets1 = await service.get_tweets_by_hashtag("python")
    assert len(tweets1) == 1
    
    # Second operation
    tweets2 = await service.get_user_tweets("alice")
    assert len(tweets2) == 1
    
    # Both should have been called
    mock_api_client.search_tweets_by_hashtag.assert_awaited_once()
    mock_api_client.get_user_tweets.assert_awaited_once()