"""Integration tests for API routes."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


@pytest.mark.integration
class TestHealthCheck:
    """Tests for health check endpoint."""

    def test_healthz_endpoint(self, test_client: TestClient):
        """Test the health check endpoint."""
        response = test_client.get("/healthz")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


@pytest.mark.integration
class TestReviewsList:
    """Tests for reviews list endpoint."""

    def test_list_reviews_default(self, test_client: TestClient):
        """Test listing reviews with default parameters."""
        response = test_client.get("/api/reviews")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "filters" in data
        assert "summary" in data
        assert "reviews" in data
        assert isinstance(data["reviews"], list)

    def test_list_reviews_with_package_name(self, test_client: TestClient):
        """Test listing reviews with package name."""
        response = test_client.get("/api/reviews?package_name=com.test.app")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["filters"]["package_name"] == "com.test.app"

    def test_list_reviews_with_page_size(self, test_client: TestClient):
        """Test listing reviews with custom page size."""
        response = test_client.get("/api/reviews?page_size=10")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["filters"]["page_size"] == 10

    def test_list_reviews_with_rating_filter(self, test_client: TestClient):
        """Test listing reviews with rating filters."""
        response = test_client.get("/api/reviews?min_rating=4&max_rating=5")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["filters"]["min_rating"] == 4
        assert data["filters"]["max_rating"] == 5

    def test_list_reviews_with_dates(self, test_client: TestClient):
        """Test listing reviews with date filters."""
        response = test_client.get(
            "/api/reviews?start_date=2024-01-01T00:00:00Z&end_date=2024-12-31T23:59:59Z"
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["filters"]["start_date"] is not None
        assert data["filters"]["end_date"] is not None

    def test_list_reviews_with_translation(self, test_client: TestClient):
        """Test listing reviews with translation language."""
        response = test_client.get("/api/reviews?translation_language=en")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["filters"]["translation_language"] == "en"

    def test_list_reviews_invalid_rating(self, test_client: TestClient):
        """Test listing reviews with invalid rating."""
        response = test_client.get("/api/reviews?min_rating=6")
        
        assert response.status_code == 422  # Validation error

    def test_list_reviews_summary_structure(self, test_client: TestClient):
        """Test that summary has correct structure."""
        response = test_client.get("/api/reviews")
        
        assert response.status_code == 200
        data = response.json()
        summary = data["summary"]
        
        assert "total_reviews" in summary
        assert "average_rating" in summary
        assert "sentiment" in summary
        assert "top_keywords" in summary
        assert "recent_reviews" in summary
        
        # Check sentiment structure
        sentiment = summary["sentiment"]
        assert "positive" in sentiment
        assert "neutral" in sentiment
        assert "negative" in sentiment

    def test_list_reviews_review_structure(self, test_client: TestClient):
        """Test that reviews have correct structure."""
        response = test_client.get("/api/reviews")
        
        assert response.status_code == 200
        data = response.json()
        reviews = data["reviews"]
        
        if len(reviews) > 0:
            review = reviews[0]
            assert "reviewId" in review
            assert "authorName" in review
            assert "comments" in review


@pytest.mark.integration
class TestGetSingleReview:
    """Tests for get single review endpoint."""

    def test_get_review(self, test_client: TestClient):
        """Test getting a single review."""
        # First get list to find a review ID
        list_response = test_client.get("/api/reviews")
        reviews = list_response.json()["reviews"]
        
        if len(reviews) > 0:
            review_id = reviews[0]["reviewId"]
            
            response = test_client.get(f"/api/reviews/{review_id}")
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["reviewId"] == review_id
            assert "authorName" in data
            assert "comments" in data

    def test_get_review_not_found(self, test_client: TestClient):
        """Test getting a non-existent review."""
        response = test_client.get("/api/reviews/non-existent-review-id")
        
        assert response.status_code == 404


@pytest.mark.integration
class TestFrontend:
    """Tests for frontend endpoints."""

    def test_homepage_loads(self, test_client: TestClient):
        """Test that the homepage loads."""
        response = test_client.get("/")
        
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        assert b"Google Play Reviews Explorer" in response.content

    def test_static_css_loads(self, test_client: TestClient):
        """Test that static CSS files are accessible."""
        response = test_client.get("/static/css/styles.css")
        
        assert response.status_code == 200
        assert "text/css" in response.headers["content-type"]

    def test_static_js_loads(self, test_client: TestClient):
        """Test that static JS files are accessible."""
        response = test_client.get("/static/js/app.js")
        
        assert response.status_code == 200
        assert "javascript" in response.headers["content-type"]

