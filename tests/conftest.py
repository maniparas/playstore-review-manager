"""Pytest configuration and shared fixtures."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Generator
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.config import Settings, get_settings
from app.main import app
from app.schemas import Comment, DeveloperComment, Review, Timestamp, UserComment


@pytest.fixture
def test_settings() -> Settings:
    """Create test settings with mock mode enabled."""
    return Settings(
        default_package_name="com.test.app",
        google_service_account_file="",
        enable_mock_mode=True,
        ai_provider=None,
        openai_api_key=None,
    )


@pytest.fixture
def mock_timestamp() -> Timestamp:
    """Create a mock timestamp."""
    return Timestamp(seconds="1731600000", nanos=0)


@pytest.fixture
def mock_user_comment(mock_timestamp: Timestamp) -> UserComment:
    """Create a mock user comment."""
    return UserComment(
        text="Great app! Love the new features.",
        originalText=None,
        lastModified=mock_timestamp,
        starRating=5,
        reviewerLanguage="en",
        device=None,
        androidOsVersion=None,
        appVersionCode=None,
        appVersionName="1.0.0",
        thumbsUpCount=10,
        thumbsDownCount=0,
        deviceMetadata=None,
    )


@pytest.fixture
def mock_developer_comment(mock_timestamp: Timestamp) -> DeveloperComment:
    """Create a mock developer comment."""
    return DeveloperComment(
        text="Thank you for your feedback!",
        lastModified=mock_timestamp,
    )


@pytest.fixture
def mock_review(
    mock_user_comment: UserComment,
    mock_developer_comment: DeveloperComment,
) -> Review:
    """Create a mock review."""
    return Review(
        reviewId="test-review-123",
        authorName="Test User",
        comments=[
            Comment(
                userComment=mock_user_comment,
                developerComment=None,
            ),
            Comment(
                userComment=None,
                developerComment=mock_developer_comment,
            ),
        ],
    )


@pytest.fixture
def mock_reviews_list(mock_review: Review) -> list[Review]:
    """Create a list of mock reviews with different ratings."""
    reviews = [mock_review]
    
    # Add a negative review
    negative_review = Review(
        reviewId="test-review-456",
        authorName="Angry User",
        comments=[
            Comment(
                userComment=UserComment(
                    text="App crashes constantly!",
                    originalText=None,
                    lastModified=Timestamp(seconds="1731600000", nanos=0),
                    starRating=1,
                    reviewerLanguage="en",
                    device=None,
                    androidOsVersion=None,
                    appVersionCode=None,
                    appVersionName="1.0.0",
                    thumbsUpCount=5,
                    thumbsDownCount=0,
                    deviceMetadata=None,
                ),
                developerComment=None,
            ),
        ],
    )
    
    # Add a neutral review
    neutral_review = Review(
        reviewId="test-review-789",
        authorName="Neutral User",
        comments=[
            Comment(
                userComment=UserComment(
                    text="It's okay, nothing special.",
                    originalText=None,
                    lastModified=Timestamp(seconds="1731600000", nanos=0),
                    starRating=3,
                    reviewerLanguage="en",
                    device=None,
                    androidOsVersion=None,
                    appVersionCode=None,
                    appVersionName="1.0.0",
                    thumbsUpCount=2,
                    thumbsDownCount=1,
                    deviceMetadata=None,
                ),
                developerComment=None,
            ),
        ],
    )
    
    reviews.extend([negative_review, neutral_review])
    return reviews


@pytest.fixture
def test_client() -> Generator[TestClient, None, None]:
    """Create a test client for the FastAPI app."""
    with TestClient(app) as client:
        yield client


@pytest.fixture(autouse=True)
def override_settings(test_settings: Settings):
    """Override application settings for tests."""
    # Clear cached settings before overriding
    get_settings.cache_clear()

    def _get_settings_override():
        return test_settings

    app.dependency_overrides[get_settings] = _get_settings_override

    yield

    app.dependency_overrides.pop(get_settings, None)
    get_settings.cache_clear()


@pytest.fixture
def mock_google_service():
    """Mock the Google API service."""
    mock_service = MagicMock()
    mock_reviews_resource = MagicMock()
    mock_service.reviews.return_value = mock_reviews_resource
    
    # Mock list response
    mock_list_request = MagicMock()
    mock_list_request.execute.return_value = {
        "reviews": [
            {
                "reviewId": "goog-review-1",
                "authorName": "Google User",
                "comments": [
                    {
                        "userComment": {
                            "text": "Excellent app!",
                            "lastModified": {"seconds": "1731600000", "nanos": 0},
                            "starRating": 5,
                            "reviewerLanguage": "en",
                            "appVersionName": "1.0.0",
                            "thumbsUpCount": 15,
                            "thumbsDownCount": 0,
                        }
                    }
                ],
            }
        ],
        "tokenPagination": {},
    }
    mock_reviews_resource.list.return_value = mock_list_request
    
    # Mock get response
    mock_get_request = MagicMock()
    mock_get_request.execute.return_value = {
        "reviewId": "goog-review-1",
        "authorName": "Google User",
        "comments": [
            {
                "userComment": {
                    "text": "Excellent app!",
                    "lastModified": {"seconds": "1731600000", "nanos": 0},
                    "starRating": 5,
                    "reviewerLanguage": "en",
                    "appVersionName": "1.0.0",
                    "thumbsUpCount": 15,
                    "thumbsDownCount": 0,
                }
            }
        ],
    }
    mock_reviews_resource.get.return_value = mock_get_request
    
    # Mock reply response
    mock_reply_request = MagicMock()
    mock_reply_request.execute.return_value = {
        "result": {
            "replyText": "Thank you!",
            "lastEdited": {"seconds": "1731700000", "nanos": 0},
        }
    }
    mock_reviews_resource.reply.return_value = mock_reply_request
    
    return mock_service


@pytest.fixture
def mock_service_account_credentials():
    """Mock service account credentials."""
    with patch("app.services.google_play_client.service_account.Credentials") as mock_creds:
        mock_creds.from_service_account_file.return_value = MagicMock()
        yield mock_creds


@pytest.fixture
def mock_build_service(mock_google_service):
    """Mock the googleapiclient.discovery.build function."""
    with patch("app.services.google_play_client.build") as mock_build:
        mock_build.return_value = mock_google_service
        yield mock_build

