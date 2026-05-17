"""Pydantic data models for fll_sdk."""

from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field


class Baby(BaseModel):
    """Baby/child model."""
    id: str
    name: str
    gender: str
    birthdate: str
    avatar: Optional[str] = None


class Task(BaseModel):
    """Task model."""
    id: str
    baby_id: str
    title: str
    description: Optional[str] = None
    tags: list[str] = Field(default_factory=list)
    type: Literal['checkin', 'learning', 'sport', 'habit'] = 'checkin'
    points: int = 0
    status: Literal['ongoing', 'paused', 'completed'] = 'ongoing'
    recurring_type: Optional[Literal['daily', 'weekly', 'monthday', 'custom']] = None
    weekdays: Optional[list[int]] = None
    completed: int = 0
    total: int = 1
    created_at: str
    updated_at: str


class Achievement(BaseModel):
    """Achievement model."""
    id: str
    baby_id: str
    name: str
    description: str
    icon: str
    unlocked_at: Optional[str] = None


class Notification(BaseModel):
    """Notification model."""
    id: str
    channel: str
    type: str
    recipient_id: str
    title: str
    content: str
    read: bool = False
    created_at: int  # timestamp


class Webhook(BaseModel):
    """Webhook subscription model."""
    id: str
    url: str
    events: list[str]
    secret: str
    active: bool = True


class WebhookEvent(BaseModel):
    """Webhook event payload received from server."""
    event: str
    data: dict
    timestamp: int