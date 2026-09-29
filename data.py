"""Utilities for FranklinWH integration."""

from dataclasses import dataclass


@dataclass
class MessageStats:
    """Message statistics for FranklinWH."""

    unread: int
    # these always pertain to the last message
    gateway_id: str
    gateway_name: str
    title: str
    content: str
    notice: str
