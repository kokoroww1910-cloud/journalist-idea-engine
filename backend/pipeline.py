from __future__ import annotations

from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Any, Dict, List
from urllib.parse import quote

import feedparser
import requests


GOOGLE_NEWS_RSS = "https://news.google.com/rss/search?q={query}&hl=zh-CN&gl=CN&ceid=CN:zh-Hans"
DEFAULT_TIMEOUT = 10
MAX_SIGNALS = 8


def _normalize_date(entry: Dict[str, Any]) -> str:
    raw_date = entry.get("published") or entry.get("updated")
    if not raw_date:
        return ""
    try:
        dt = parsedate_to_datetime(raw_date)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc).isoformat()
    except (TypeError, ValueError, IndexError):
        return ""


def _normalize_entry(entry: Dict[str, Any]) -> Dict[str, str]:
    source_name = "未知来源"
    if isinstance(entry.get("source"), dict):
        source_name = entry["source"].get("title") or source_name

    return {
        "title": (entry.get("title") or "").strip(),
        "source": source_name,
        "url": (entry.get("link") or "").strip(),
        "published_date": _normalize_date(entry),
    }


def _is_valid_signal(signal: Dict[str, str]) -> bool:
    return bool(signal["title"] and signal["url"])


def fetch_news_signals(topic: str, limit: int = MAX_SIGNALS) -> List[Dict[str, str]]:
    """Fetch real RSS signals, return normalized list with graceful fallback."""
    query = quote(topic)
    rss_url = GOOGLE_NEWS_RSS.format(query=query)

    try:
        response = requests.get(rss_url, timeout=DEFAULT_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException:
        return []

    parsed = feedparser.parse(response.content)
    entries = parsed.get("entries", [])

    signals: List[Dict[str, str]] = []
    seen_urls = set()

    for entry in entries:
        normalized = _normalize_entry(entry)
        if not _is_valid_signal(normalized):
            continue
        if normalized["url"] in seen_urls:
            continue
        seen_urls.add(normalized["url"])
        signals.append(normalized)
        if len(signals) >= max(5, min(limit, 10)):
            break

    return signals


def score_signals(signals: List[Dict[str, str]]) -> Dict[str, int]:
    """Deterministic, explainable scoring for impact and potential."""
    major_media = {"新华社", "人民网", "央视网", "财新网", "第一财经", "澎湃新闻"}

    signal_count = len(signals)
    unique_sources = len({item["source"] for item in signals if item.get("source")})
    major_hits = sum(1 for item in signals if item.get("source") in major_media)

    now = datetime.now(timezone.utc)
    recent_count = 0
    for item in signals:
        try:
            dt = datetime.fromisoformat(item["published_date"])
            if (now - dt).total_seconds() <= 72 * 3600:
                recent_count += 1
        except (ValueError, TypeError):
            continue

    impact_score = min(100, signal_count * 8 + unique_sources * 6 + major_hits * 10 + 20)

    repeated_titles = signal_count - len({item["title"][:15] for item in signals})
    trend_factor = max(0, signal_count - 3)
    potential_score = min(100, recent_count * 12 + repeated_titles * 8 + trend_factor * 6 + 25)

    return {
        "impact_score": impact_score,
        "potential_score": potential_score,
    }
