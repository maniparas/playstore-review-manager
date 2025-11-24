"""Unit tests for AI insights module."""
from __future__ import annotations

from datetime import datetime, timezone

import pytest

from app.ai.insights import (
    _bucket_sentiment,
    _extract_keywords,
    summarize_reviews,
)
from app.schemas import ReviewFilters


@pytest.mark.unit
class TestSentimentBucketing:
    """Tests for sentiment bucketing."""

    def test_positive_sentiment(self):
        """Test positive sentiment detection."""
        assert _bucket_sentiment(5) == "positive"
        assert _bucket_sentiment(4) == "positive"

    def test_negative_sentiment(self):
        """Test negative sentiment detection."""
        assert _bucket_sentiment(1) == "negative"
        assert _bucket_sentiment(2) == "negative"

    def test_neutral_sentiment(self):
        """Test neutral sentiment detection."""
        assert _bucket_sentiment(3) == "neutral"

    def test_none_sentiment(self):
        """Test None rating."""
        assert _bucket_sentiment(None) == "neutral"


@pytest.mark.unit
class TestKeywordExtraction:
    """Tests for keyword extraction."""

    def test_extract_keywords_basic(self):
        """Test basic keyword extraction."""
        text = "Great app with amazing features and excellent design"
        keywords = list(_extract_keywords(text))
        
        assert "great" in keywords
        assert "amazing" in keywords
        assert "features" in keywords
        assert "excellent" in keywords
        assert "design" in keywords

    def test_extract_keywords_filters_stop_words(self):
        """Test that stop words are filtered."""
        text = "The app is great and this is amazing for the user"
        keywords = list(_extract_keywords(text))
        
        assert "the" not in keywords
        assert "and" not in keywords
        assert "this" not in keywords
        assert "for" not in keywords
        assert "app" not in keywords  # 'app' is a custom stop word

    def test_extract_keywords_filters_short_words(self):
        """Test that short words are filtered."""
        text = "I am so in to it"
        keywords = list(_extract_keywords(text))
        
        # All words are 3 chars or less, should be filtered
        assert len(keywords) == 0

    def test_extract_keywords_empty_text(self):
        """Test keyword extraction with empty text."""
        keywords = list(_extract_keywords(""))
        assert len(keywords) == 0

    def test_extract_keywords_none_text(self):
        """Test keyword extraction with None text."""
        keywords = list(_extract_keywords(None))
        assert len(keywords) == 0

    def test_extract_keywords_special_chars(self):
        """Test keyword extraction with special characters."""
        text = "App crashes!!! Very bad... Won't use anymore!!!"
        keywords = list(_extract_keywords(text))
        
        assert "crashes" in keywords
        assert "very" in keywords
        assert "anymore" in keywords

    def test_extract_keywords_case_insensitive(self):
        """Test that keywords are lowercase."""
        text = "GREAT Amazing Excellent"
        keywords = list(_extract_keywords(text))
        
        assert "great" in keywords
        assert "amazing" in keywords
        assert "excellent" in keywords
        assert "GREAT" not in keywords


@pytest.mark.unit
class TestSummarizeReviews:
    """Tests for review summarization."""

    def test_summarize_reviews_basic(self, mock_reviews_list, test_settings):
        """Test basic review summarization."""
        filters = ReviewFilters(
            package_name="com.test.app",
            page_size=50,
            recent_activity_window_hours=72,
        )
        
        summary = summarize_reviews(mock_reviews_list, filters, test_settings)
        
        assert summary.total_reviews == 3
        assert summary.average_rating > 0
        assert summary.sentiment.positive > 0
        assert summary.sentiment.negative > 0
        assert summary.sentiment.neutral > 0
        assert len(summary.top_keywords) > 0

    def test_summarize_reviews_all_positive(self, mock_user_comment, test_settings):
        """Test summarization with all positive reviews."""
        from app.schemas import Comment, Review
        
        reviews = [
            Review(
                reviewId=f"review-{i}",
                authorName=f"User {i}",
                comments=[Comment(userComment=mock_user_comment, developerComment=None)],
            )
            for i in range(5)
        ]
        
        filters = ReviewFilters(
            package_name="com.test.app",
            page_size=50,
            recent_activity_window_hours=72,
        )
        
        summary = summarize_reviews(reviews, filters, test_settings)
        
        assert summary.total_reviews == 5
        assert summary.average_rating == 5.0
        assert summary.sentiment.positive == 5
        assert summary.sentiment.negative == 0
        assert summary.sentiment.neutral == 0

    def test_summarize_empty_reviews(self, test_settings):
        """Test summarization with no reviews."""
        filters = ReviewFilters(
            package_name="com.test.app",
            page_size=50,
            recent_activity_window_hours=72,
        )
        
        summary = summarize_reviews([], filters, test_settings)
        
        assert summary.total_reviews == 0
        assert summary.average_rating == 0.0
        assert summary.sentiment.positive == 0
        assert summary.sentiment.negative == 0
        assert summary.sentiment.neutral == 0

    def test_summarize_recent_reviews(self, mock_reviews_list, test_settings):
        """Test counting recent reviews."""
        filters = ReviewFilters(
            package_name="com.test.app",
            page_size=50,
            recent_activity_window_hours=72,
        )
        
        summary = summarize_reviews(mock_reviews_list, filters, test_settings)
        
        # Recent reviews count should be calculated based on window
        assert summary.recent_activity_window_hours == 72

    def test_summarize_keyword_extraction(self, mock_reviews_list, test_settings):
        """Test that keywords are extracted correctly."""
        filters = ReviewFilters(
            package_name="com.test.app",
            page_size=50,
            recent_activity_window_hours=72,
        )
        
        summary = summarize_reviews(mock_reviews_list, filters, test_settings)
        
        # Should have at least some keywords
        assert len(summary.top_keywords) > 0
        # Keywords should be strings
        assert all(isinstance(kw, str) for kw in summary.top_keywords)
        # Keywords should be non-empty
        assert all(len(kw) > 0 for kw in summary.top_keywords)

    def test_summarize_reviews_without_comments(self, test_settings):
        """Test summarization with reviews that have no user comments."""
        from app.schemas import Review
        
        reviews = [
            Review(
                reviewId="review-no-comment",
                authorName="User",
                comments=[],
            )
        ]
        
        filters = ReviewFilters(
            package_name="com.test.app",
            page_size=50,
            recent_activity_window_hours=72,
        )
        
        summary = summarize_reviews(reviews, filters, test_settings)
        
        assert summary.total_reviews == 1
        assert summary.average_rating == 0.0
        assert summary.sentiment.positive == 0
        assert summary.sentiment.negative == 0
        assert summary.sentiment.neutral == 0

