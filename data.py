"""Utilities for FranklinWH integration."""

from dataclasses import dataclass


@dataclass
class MessageStats:
    """Message statistics for FranklinWH."""

    unread: int
    last: str
