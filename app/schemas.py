"""Pydantic schemas shared between the API layer and templates."""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class Timestamp(BaseModel):
    seconds: Optional[str] = None
    nanos: Optional[int] = None

    def to_datetime(self) -> Optional[datetime]:
        if self.seconds is None:
            return None
        seconds_int = int(self.seconds)
        nanos = self.nanos or 0
        return datetime.utcfromtimestamp(seconds_int + nanos / 1_000_000_000)


class DeviceMetadata(BaseModel):
    productName: Optional[str] = None
    manufacturer: Optional[str] = None
    deviceClass: Optional[str] = None
    screenWidthPx: Optional[int] = None
    screenHeightPx: Optional[int] = None
    nativePlatform: Optional[str] = None
    screenDensityDpi: Optional[int] = None
    glEsVersion: Optional[int] = None
    cpuModel: Optional[str] = None
    cpuMake: Optional[str] = None
    ramMb: Optional[int] = None


class UserComment(BaseModel):
    text: Optional[str] = None
    originalText: Optional[str] = None
    lastModified: Optional[Timestamp] = None
    starRating: Optional[int] = None
    reviewerLanguage: Optional[str] = None
    device: Optional[str] = None
    androidOsVersion: Optional[int] = None
    appVersionCode: Optional[int] = None
    appVersionName: Optional[str] = None
    thumbsUpCount: Optional[int] = 0
    thumbsDownCount: Optional[int] = 0
    deviceMetadata: Optional[DeviceMetadata] = None


class DeveloperComment(BaseModel):
    text: Optional[str] = None
    lastModified: Optional[Timestamp] = None


class Comment(BaseModel):
    userComment: Optional[UserComment] = None
    developerComment: Optional[DeveloperComment] = None


class Review(BaseModel):
    reviewId: str
    authorName: Optional[str] = None
    comments: List[Comment] = Field(default_factory=list)

    @property
    def latest_user_comment(self) -> Optional[UserComment]:
        for comment in self.comments:
            if comment.userComment:
                return comment.userComment
        return None

    @property
    def latest_developer_comment(self) -> Optional[DeveloperComment]:
        for comment in self.comments:
            if comment.developerComment:
                return comment.developerComment
        return None


class ReviewFilters(BaseModel):
    package_name: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    min_rating: Optional[int] = None
    max_rating: Optional[int] = None
    translation_language: Optional[str] = None
    page_size: int = 50
    recent_activity_window_hours: int = 72


class SentimentSplit(BaseModel):
    positive: int = 0
    neutral: int = 0
    negative: int = 0


class ReviewSummary(BaseModel):
    total_reviews: int
    average_rating: float
    sentiment: SentimentSplit
    top_keywords: List[str]
    recent_activity_window_hours: int = 72
    recent_reviews: int = 0
    ai_brief: Optional[str] = None


class ReviewsResponse(BaseModel):
    filters: ReviewFilters
    summary: ReviewSummary
    reviews: List[Review]
