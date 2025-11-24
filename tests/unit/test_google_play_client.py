"""Unit tests for Google Play Review Client."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from app.schemas import Review
from app.services.google_play_client import GooglePlayReviewClient


@pytest.mark.unit
class TestGooglePlayReviewClient:
    """Tests for GooglePlayReviewClient."""

    def test_client_initialization(self, test_settings):
        """Test client initialization."""
        client = GooglePlayReviewClient(test_settings)
        assert client.settings == test_settings
        assert client._service is None
        assert client._mock_reviews is None

    def test_list_reviews_mock_mode(self, test_settings):
        """Test listing reviews in mock mode."""
        client = GooglePlayReviewClient(test_settings)
        reviews = client.list_reviews(
            package_name="com.test.app",
            page_size=10,
        )
        
        assert isinstance(reviews, list)
        assert len(reviews) > 0
        assert all(isinstance(r, Review) for r in reviews)

    def test_get_review_mock_mode(self, test_settings):
        """Test getting a single review in mock mode."""
        client = GooglePlayReviewClient(test_settings)
        review = client.get_review(
            package_name="com.test.app",
            review_id="mock-review-1",
        )
        
        assert isinstance(review, Review)
        assert review.reviewId == "mock-review-1"
        assert review.authorName is not None

    def test_get_review_not_found_mock_mode(self, test_settings):
        """Test getting a non-existent review in mock mode."""
        client = GooglePlayReviewClient(test_settings)
        review = client.get_review(
            package_name="com.test.app",
            review_id="non-existent-review",
        )
        
        assert review is None

    @patch("app.services.google_play_client.service_account.Credentials")
    @patch("app.services.google_play_client.build")
    def test_list_reviews_real_api(
        self,
        mock_build,
        mock_creds,
        mock_google_service,
    ):
        """Test listing reviews with real API (mocked)."""
        from app.config import Settings
        
        test_settings = Settings(
            enable_mock_mode=False,
            google_service_account_file="test_key.json",
        )
        
        mock_build.return_value = mock_google_service
        mock_creds.from_service_account_file.return_value = MagicMock()
        
        # Create a temporary key file
        key_file = Path("test_key.json")
        key_file.write_text('{"type": "service_account"}')
        
        try:
            client = GooglePlayReviewClient(test_settings)
            reviews = client.list_reviews(
                package_name="com.test.app",
                page_size=10,
            )
            
            assert isinstance(reviews, list)
            assert len(reviews) > 0
            mock_google_service.reviews().list.assert_called_once()
        finally:
            if key_file.exists():
                key_file.unlink()

    @patch("app.services.google_play_client.service_account.Credentials")
    @patch("app.services.google_play_client.build")
    def test_get_review_real_api(
        self,
        mock_build,
        mock_creds,
        mock_google_service,
    ):
        """Test getting a review with real API (mocked)."""
        from app.config import Settings
        
        test_settings = Settings(
            enable_mock_mode=False,
            google_service_account_file="test_key.json",
        )
        
        mock_build.return_value = mock_google_service
        mock_creds.from_service_account_file.return_value = MagicMock()
        
        key_file = Path("test_key.json")
        key_file.write_text('{"type": "service_account"}')
        
        try:
            client = GooglePlayReviewClient(test_settings)
            review = client.get_review(
                package_name="com.test.app",
                review_id="goog-review-1",
            )
            
            assert isinstance(review, Review)
            assert review.reviewId == "goog-review-1"
            mock_google_service.reviews().get.assert_called_once()
        finally:
            if key_file.exists():
                key_file.unlink()

    def test_pagination_handling(self):
        """Test that pagination is handled correctly."""
        from app.config import Settings
        
        test_settings = Settings(
            enable_mock_mode=False,
            google_service_account_file="test_key.json",
        )
        
        with patch("app.services.google_play_client.service_account.Credentials"), \
             patch("app.services.google_play_client.build") as mock_build:
            
            # Create mock service with pagination
            mock_service = MagicMock()
            mock_reviews_resource = MagicMock()
            
            # First page
            mock_request_1 = MagicMock()
            mock_request_1.execute.return_value = {
                "reviews": [{"reviewId": "review-1", "authorName": "User 1", "comments": []}],
                "tokenPagination": {"nextPageToken": "token123"},
            }
            
            # Second page (last page)
            mock_request_2 = MagicMock()
            mock_request_2.execute.return_value = {
                "reviews": [{"reviewId": "review-2", "authorName": "User 2", "comments": []}],
                "tokenPagination": {},
            }
            
            mock_reviews_resource.list.side_effect = [mock_request_1, mock_request_2]
            mock_service.reviews.return_value = mock_reviews_resource
            mock_build.return_value = mock_service
            
            key_file = Path("test_key.json")
            key_file.write_text('{"type": "service_account"}')
            
            try:
                client = GooglePlayReviewClient(test_settings)
                reviews = client.list_reviews(
                    package_name="com.test.app",
                    page_size=10,
                )
                
                assert len(reviews) == 2
                assert reviews[0].reviewId == "review-1"
                assert reviews[1].reviewId == "review-2"
                # Verify list was called twice for pagination
                assert mock_reviews_resource.list.call_count == 2
            finally:
                if key_file.exists():
                    key_file.unlink()

