"""Utilities for FranklinWH integration."""

from dataclasses import dataclass
from typing import Any

type Message = dict[str, Any]


@dataclass
class MessageStats:
    """Message statistics for FranklinWH."""

    unread: int
