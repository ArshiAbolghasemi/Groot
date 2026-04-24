import json
import logging
from typing import Any

import httpx
from langchain_core.tools import tool
from tenacity import (
    before_sleep_log,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from groot.shared.config.settings import settings

logger = logging.getLogger(__name__)

RETRYABLE_WIKIPEDIA_EXCEPTIONS = (
    httpx.ConnectError,  # TCP connection refused or DNS failure
    httpx.HTTPStatusError,  # 4xx/5xx response (raised by raise_for_status)
    httpx.ReadError,  # Connection dropped mid-response body
    httpx.ReadTimeout,  # Server accepted but didn't respond in time
    httpx.RemoteProtocolError,  # Server sent malformed HTTP
)


@retry(
    stop=stop_after_attempt(settings.wikipedia_reqest_retry_attempt),
    wait=wait_exponential(
        multiplier=2,
        min=settings.wikipedia_request_retry_min_wait,
        max=settings.wikipedia_request_retry_max_wait,
    ),
    retry=retry_if_exception_type(RETRYABLE_WIKIPEDIA_EXCEPTIONS),
    before_sleep=before_sleep_log(logger, logging.WARNING),
    reraise=True,
)
def _search_wikipedia(query: str) -> list[dict[str, Any]]:
    params = {
        "action": "query",
        "list": "search",
        "srsearch": query,
        "format": "json",
        "utf8": 1,
        "srlimit": settings.wikipedia_search_result_limit,
    }
    client_kwargs = {
        "timeout": settings.wikipedia_request_timeout_seconds,
        "proxy": settings.wikipedia_proxy_url,
    }

    with httpx.Client(
        **client_kwargs, headers={"User-Agent": settings.wikipedia_user_agent}
    ) as client:
        response = client.get(settings.wikipedia_search_url, params=params)
        response.raise_for_status()
        payload = response.json()

    results = payload.get("query", {}).get("search", [])
    return [
        {
            "title": item.get("title", ""),
            "snippet": item.get("snippet", ""),
            "pageid": item.get("pageid"),
        }
        for item in results
    ]


@tool("wikipedia_search")
def wikipedia_search(query: str) -> str:
    """Search Wikipedia for factual background when the answer needs external knowledge."""
    logger.info("Calling Wikipedia tool")
    results = _search_wikipedia(query)
    return json.dumps(results, ensure_ascii=False)
