"""Utility helpers to generate lightweight insights about the reviews."""
from __future__ import annotations

import logging
from collections import Counter
from datetime import datetime, timezone
from typing import Iterable, Optional

from ..config import Settings
from ..schemas import Review, ReviewFilters, ReviewSummary, SentimentSplit

logger = logging.getLogger(__name__)


def _bucket_sentiment(star_rating: Optional[int]) -> str:
    if star_rating is None:
        return "neutral"
    if star_rating >= 4:
        return "positive"
    if star_rating <= 2:
        return "negative"
    return "neutral"


def _extract_keywords(text: Optional[str]) -> Iterable[str]:
    if not text:
        return []
    sanitized = "".join(ch.lower() if ch.isalnum() or ch.isspace() else " " for ch in text)
    stop_words = {
        "the",
        "and",
        "for",
        "with",
        "this",
        "that",
        "have",
        "has",
        "was",
        "were",
        "but",
        "not",
        "app",
    }
    return [token for token in sanitized.split() if len(token) > 3 and token not in stop_words]


def _maybe_ai_brief(reviews: list[Review], settings: Settings) -> Optional[str]:
    if not settings.ai_provider:
        return None

    snippets = []
    for review in reviews[:20]:
        user_comment = review.latest_user_comment
        if user_comment and user_comment.text:
            snippets.append(f"- {user_comment.starRating or '?'}★ {user_comment.text[:280]}")

    if not snippets:
        return None

    content = "\n".join(snippets)

    if settings.ai_provider.lower() == "openai":
        try:
            from openai import OpenAI
        except Exception as exc:  # pragma: no cover - optional dependency
            logger.warning("OpenAI SDK missing: %s", exc)
            return None

        if not settings.openai_api_key:
            logger.warning("OPENAI_API_KEY not configured; skipping AI brief")
            return None

        client = OpenAI(api_key=settings.openai_api_key)
        prompt = (
            "Summarize recurring themes from Google Play reviews. "
            "Highlight biggest blockers and wins in under 120 words."
        )
        try:
            response = client.responses.create(
                model="gpt-4o-mini",
                input=[
                    {
                        "role": "system",
                        "content": prompt,
                    },
                    {
                        "role": "user",
                        "content": content,
                    },
                ],
            )
            ai_text = response.output[0].content[0].text
            return ai_text.strip()
        except Exception as exc:  # pragma: no cover - network
            logger.warning("AI brief generation failed: %s", exc)
            return None

    logger.info("Unsupported AI provider '%s'", settings.ai_provider)
    return None


def summarize_reviews(
    reviews: list[Review],
    filters: ReviewFilters,
    settings: Settings,
) -> ReviewSummary:
    total = len(reviews)
    ratings = [review.latest_user_comment.starRating for review in reviews if review.latest_user_comment and review.latest_user_comment.starRating]
    average_rating = round(sum(ratings) / len(ratings), 2) if ratings else 0.0

    sentiment_counter = Counter()
    keyword_counter = Counter()
    now = datetime.now(timezone.utc)
    recent_reviews = 0

    for review in reviews:
        user_comment = review.latest_user_comment
        if not user_comment:
            continue
        sentiment_bucket = _bucket_sentiment(user_comment.starRating)
        sentiment_counter[sentiment_bucket] += 1

        keywords = _extract_keywords(user_comment.text)
        keyword_counter.update(keywords)

        last_modified = (
            user_comment.lastModified.to_datetime() if user_comment.lastModified else None
        )
        if last_modified:
            last_modified = last_modified.replace(tzinfo=timezone.utc)
            delta_hours = (now - last_modified).total_seconds() / 3600
            if delta_hours <= filters.recent_activity_window_hours:
                recent_reviews += 1

    sentiment = SentimentSplit(
        positive=sentiment_counter.get("positive", 0),
        neutral=sentiment_counter.get("neutral", 0),
        negative=sentiment_counter.get("negative", 0),
    )

    ai_brief = _maybe_ai_brief(reviews, settings)

    return ReviewSummary(
        total_reviews=total,
        average_rating=average_rating,
        sentiment=sentiment,
        top_keywords=[keyword for keyword, _ in keyword_counter.most_common(8)],
        recent_activity_window_hours=filters.recent_activity_window_hours,
        recent_reviews=recent_reviews,
        ai_brief=ai_brief,
    )
