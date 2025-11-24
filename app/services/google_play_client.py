"""Client wrapper around the Google Play Developer Reviews API."""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Dict, Iterable, List, Optional

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from ..config import Settings
from ..schemas import Review

# Configure logger with custom formatting
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
MOCK_REVIEWS_PATH = Path("sample_data/mock_reviews.json")


class GooglePlayReviewClient:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._service = None
        self._mock_reviews: Optional[List[Review]] = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def list_reviews(
        self,
        package_name: str,
        page_size: int,
        translation_language: Optional[str] = None,
    ) -> List[Review]:
        logger.info("="*80)
        logger.info("📥 INCOMING REQUEST: list_reviews()")
        logger.info("-"*80)
        logger.info(f"  Package Name: {package_name}")
        logger.info(f"  Page Size: {page_size}")
        logger.info(f"  Translation Language: {translation_language or 'None'}")
        logger.info(f"  Mock Mode: {self.settings.enable_mock_mode}")
        logger.info("="*80)
        
        if self.settings.enable_mock_mode:
            logger.info("🔧 Using MOCK data (no Google API call)")
            reviews = self._list_mock_reviews()
            logger.info(f"✅ Returned {len(reviews)} mock reviews")
            return reviews

        raw_reviews = list(
            self._iterate_reviews_api(
                package_name=package_name,
                page_size=page_size,
                translation_language=translation_language,
            )
        )
        validated_reviews = [Review.model_validate(review) for review in raw_reviews]
        
        logger.info("="*80)
        logger.info(f"✅ Successfully fetched {len(validated_reviews)} reviews from Google Play")
        logger.info("="*80)
        
        return validated_reviews

    def get_review(self, package_name: str, review_id: str) -> Optional[Review]:
        logger.info("="*80)
        logger.info("📥 INCOMING REQUEST: get_review()")
        logger.info("-"*80)
        logger.info(f"  Package Name: {package_name}")
        logger.info(f"  Review ID: {review_id}")
        logger.info(f"  Mock Mode: {self.settings.enable_mock_mode}")
        logger.info("="*80)
        
        if self.settings.enable_mock_mode:
            logger.info("🔧 Using MOCK data (no Google API call)")
            mock_reviews = self._list_mock_reviews()
            for review in mock_reviews:
                if review.reviewId == review_id:
                    logger.info(f"✅ Found mock review: {review_id}")
                    return review
            logger.warning(f"⚠️  Mock review not found: {review_id}")
            return None

        service = self._build_service()
        
        logger.info("🌐 OUTGOING REQUEST to Google Play API")
        logger.info(f"  → GET /applications/{package_name}/reviews/{review_id}")
        
        try:
            # Calls: GET https://androidpublisher.googleapis.com/androidpublisher/v3/
            #        applications/{packageName}/reviews/{reviewId}
            response = (
                service.reviews()
                .get(packageName=package_name, reviewId=review_id)
                .execute()
            )
            
            logger.info("📦 RESPONSE from Google Play API")
            logger.info(f"  Review ID: {response.get('reviewId', 'N/A')}")
            logger.info(f"  Author: {response.get('authorName', 'N/A')}")
            logger.info(f"  Comments Count: {len(response.get('comments', []))}")
            logger.info(f"✅ Successfully fetched review: {review_id}")
            
        except HttpError as exc:  # pragma: no cover - network
            logger.error("="*80)
            logger.error(f"❌ Google Play get() FAILED: {exc}")
            logger.error("="*80)
            raise
            
        return Review.model_validate(response)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _build_service(self):
        if self._service is not None:
            return self._service

        service_account_path = self.settings.google_service_account_file
        if not service_account_path or service_account_path.startswith("TODO"):
            raise RuntimeError(
                "google_service_account_file is not configured. "
                "Update .env or set the environment variable."
            )

        credentials = service_account.Credentials.from_service_account_file(
            service_account_path,
            scopes=self.settings.google_play_scopes,
        )
        # Build the Google Play Developer API service client.
        # This automatically configures the correct base URL:
        # https://androidpublisher.googleapis.com/androidpublisher/v3/
        self._service = build(
            "androidpublisher",  # Service name
            "v3",                # API version
            credentials=credentials,
            cache_discovery=False,
        )
        return self._service

    def _iterate_reviews_api(
        self,
        package_name: str,
        page_size: int,
        translation_language: Optional[str] = None,
    ) -> Iterable[Dict]:
        service = self._build_service()
        max_results = min(max(page_size, 1), 100)
        
        page_num = 1
        total_fetched = 0
        
        # Calls: GET https://androidpublisher.googleapis.com/androidpublisher/v3/
        #        applications/{packageName}/reviews?maxResults={max_results}
        request = service.reviews().list(
            packageName=package_name,
            translationLanguage=translation_language,
            maxResults=max_results,
        )

        while request is not None:
            logger.info("🌐 OUTGOING REQUEST to Google Play API")
            logger.info(f"  → GET /applications/{package_name}/reviews")
            logger.info(f"  Parameters:")
            logger.info(f"    - maxResults: {max_results}")
            logger.info(f"    - translationLanguage: {translation_language or 'None'}")
            logger.info(f"    - page: {page_num}")
            
            try:
                response = request.execute()
                
                reviews_in_page = response.get("reviews", [])
                reviews_count = len(reviews_in_page)
                total_fetched += reviews_count
                
                logger.info("📦 RESPONSE from Google Play API")
                logger.info(f"  Reviews in this page: {reviews_count}")
                logger.info(f"  Total fetched so far: {total_fetched}")
                
                # Pretty print first review as sample
                if reviews_in_page and page_num == 1:
                    sample = reviews_in_page[0]
                    logger.info("  Sample Review (first one):")
                    logger.info(f"    - ID: {sample.get('reviewId', 'N/A')}")
                    logger.info(f"    - Author: {sample.get('authorName', 'N/A')}")
                    comments = sample.get('comments', [])
                    if comments and comments[0].get('userComment'):
                        user_comment = comments[0]['userComment']
                        rating = user_comment.get('starRating', 'N/A')
                        text = user_comment.get('text', '')[:80]
                        logger.info(f"    - Rating: {rating}★")
                        logger.info(f"    - Text: {text}{'...' if len(user_comment.get('text', '')) > 80 else ''}")
                
            except HttpError as exc:  # pragma: no cover - network
                logger.error("="*80)
                logger.error(f"❌ Google Play list() FAILED on page {page_num}")
                logger.error(f"  Error: {exc}")
                logger.error("="*80)
                raise

            yield from reviews_in_page
            
            # Handle pagination using token from response
            token_pagination = response.get("tokenPagination", {})
            next_token = token_pagination.get("nextPageToken")
            
            if next_token:
                logger.info(f"  → Has more pages, fetching next...")
                logger.info(f"  → Next page token: {next_token[:20]}...")
                page_num += 1
                request = service.reviews().list(
                    packageName=package_name,
                    translationLanguage=translation_language,
                    maxResults=max_results,
                    token=next_token,
                )
            else:
                logger.info(f"  ✅ No more pages. Total reviews fetched: {total_fetched}")
                request = None

    def _list_mock_reviews(self) -> List[Review]:
        if self._mock_reviews is not None:
            return self._mock_reviews

        if not MOCK_REVIEWS_PATH.exists():
            logger.warning("Mock data file missing at %s", MOCK_REVIEWS_PATH)
            self._mock_reviews = []
            return self._mock_reviews

        with MOCK_REVIEWS_PATH.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
        self._mock_reviews = [Review.model_validate(review) for review in payload]
        return self._mock_reviews
