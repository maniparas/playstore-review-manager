"""FastAPI routes for serving reviews and insights."""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request

from ..ai.insights import summarize_reviews
from ..config import Settings, get_settings
from ..schemas import Review, ReviewFilters, ReviewsResponse
from ..services.google_play_client import GooglePlayReviewClient

router = APIRouter()
logger = logging.getLogger(__name__)


def get_client(settings: Settings = Depends(get_settings)) -> GooglePlayReviewClient:
    return GooglePlayReviewClient(settings)


def _parse_date(raw: Optional[str]) -> Optional[datetime]:
    if not raw:
        return None
    try:
        parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        if parsed.tzinfo:
            return parsed.astimezone(timezone.utc).replace(tzinfo=None)
        return parsed
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {raw}") from exc


def _filter_reviews(reviews: list[Review], filters: ReviewFilters) -> list[Review]:
    filtered: list[Review] = []
    for review in reviews:
        user_comment = review.latest_user_comment
        if not user_comment:
            continue

        last_modified = (
            user_comment.lastModified.to_datetime() if user_comment.lastModified else None
        )
        if filters.start_date and (not last_modified or last_modified < filters.start_date):
            continue
        if filters.end_date and (not last_modified or last_modified > filters.end_date):
            continue

        if filters.min_rating and (
            not user_comment.starRating or user_comment.starRating < filters.min_rating
        ):
            continue
        if filters.max_rating and (
            not user_comment.starRating or user_comment.starRating > filters.max_rating
        ):
            continue

        filtered.append(review)
    return filtered


@router.get("/api/reviews", response_model=ReviewsResponse)
def list_reviews(
    request: Request,
    package_name: Optional[str] = Query(None, description="Android package name"),
    start_date: Optional[str] = Query(None, description="ISO 8601 start date"),
    end_date: Optional[str] = Query(None, description="ISO 8601 end date"),
    min_rating: Optional[int] = Query(None, ge=1, le=5),
    max_rating: Optional[int] = Query(None, ge=1, le=5),
    translation_language: Optional[str] = Query(None, min_length=2, max_length=5),
    page_size: int = Query(50, ge=1, le=500),
    recent_window_hours: int = Query(72, ge=1, le=720),
    client: GooglePlayReviewClient = Depends(get_client),
    settings: Settings = Depends(get_settings),
) -> ReviewsResponse:
    logger.info("="*100)
    logger.info("🌍 INCOMING HTTP REQUEST from Client")
    logger.info("-"*100)
    logger.info(f"  Method: {request.method}")
    logger.info(f"  URL: {request.url}")
    logger.info(f"  Client: {request.client.host if request.client else 'Unknown'}")
    logger.info("  Query Parameters:")
    logger.info(f"    - package_name: {package_name}")
    logger.info(f"    - start_date: {start_date}")
    logger.info(f"    - end_date: {end_date}")
    logger.info(f"    - min_rating: {min_rating}")
    logger.info(f"    - max_rating: {max_rating}")
    logger.info(f"    - translation_language: {translation_language}")
    logger.info(f"    - page_size: {page_size}")
    logger.info(f"    - recent_window_hours: {recent_window_hours}")
    logger.info("="*100)
    resolved_package = package_name or settings.default_package_name
    if not resolved_package:
        raise HTTPException(status_code=400, detail="package_name is required")

    filters = ReviewFilters(
        package_name=resolved_package,
        start_date=_parse_date(start_date),
        end_date=_parse_date(end_date),
        min_rating=min_rating,
        max_rating=max_rating,
        translation_language=translation_language or settings.default_translation_language,
        page_size=page_size,
        recent_activity_window_hours=recent_window_hours,
    )

    reviews = client.list_reviews(
        package_name=filters.package_name,
        page_size=filters.page_size,
        translation_language=filters.translation_language,
    )

    filtered_reviews = _filter_reviews(reviews, filters)
    logger.info(f"  🔍 Applied filters: {len(reviews)} → {len(filtered_reviews)} reviews")
    
    summary = summarize_reviews(filtered_reviews, filters, settings)
    
    response_data = ReviewsResponse(filters=filters, summary=summary, reviews=filtered_reviews)
    
    logger.info("="*100)
    logger.info("📤 OUTGOING HTTP RESPONSE to Client")
    logger.info("-"*100)
    logger.info(f"  Status: 200 OK")
    logger.info(f"  Total Reviews: {summary.total_reviews}")
    logger.info(f"  Average Rating: {summary.average_rating}★")
    logger.info(f"  Sentiment: +{summary.sentiment.positive} ={summary.sentiment.neutral} -{summary.sentiment.negative}")
    logger.info(f"  Keywords: {', '.join(summary.top_keywords[:5])}")
    logger.info("="*100)
    
    return response_data


@router.get("/api/reviews/{review_id}", response_model=Review)
def get_review(
    request: Request,
    review_id: str,
    package_name: Optional[str] = Query(None),
    client: GooglePlayReviewClient = Depends(get_client),
    settings: Settings = Depends(get_settings),
) -> Review:
    logger.info("="*100)
    logger.info("🌍 INCOMING HTTP REQUEST from Client")
    logger.info("-"*100)
    logger.info(f"  Method: {request.method}")
    logger.info(f"  URL: {request.url}")
    logger.info(f"  Client: {request.client.host if request.client else 'Unknown'}")
    logger.info(f"  Path Parameters:")
    logger.info(f"    - review_id: {review_id}")
    logger.info(f"  Query Parameters:")
    logger.info(f"    - package_name: {package_name}")
    logger.info("="*100)
    
    resolved_package = package_name or settings.default_package_name
    if not resolved_package:
        raise HTTPException(status_code=400, detail="package_name is required")

    review = client.get_review(resolved_package, review_id)
    if not review:
        logger.warning(f"⚠️  Review not found: {review_id}")
        raise HTTPException(status_code=404, detail="Review not found")
    
    logger.info("="*100)
    logger.info("📤 OUTGOING HTTP RESPONSE to Client")
    logger.info("-"*100)
    logger.info(f"  Status: 200 OK")
    logger.info(f"  Review ID: {review.reviewId}")
    logger.info(f"  Author: {review.authorName}")
    logger.info("="*100)
    
    return review
