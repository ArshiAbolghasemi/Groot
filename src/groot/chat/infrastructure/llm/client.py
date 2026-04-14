import logging
from collections.abc import Callable, Iterator
from typing import TypeVar

import httpx
from langchain_openai import ChatOpenAI
from openai import APIConnectionError, APIError, APITimeoutError, RateLimitError
from pydantic import SecretStr
from tenacity import (
    Retrying,
    before_sleep_log,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from groot.chat.infrastructure.llm.error import PartialStreamError
from groot.shared.config.settings import settings

logger = logging.getLogger(__name__)

T = TypeVar("T")

RETRYABLE_LLM_EXCEPTIONS = (
    APIConnectionError,
    APIError,
    APITimeoutError,
    RateLimitError,
    httpx.ConnectError,
    httpx.ReadError,
    httpx.ReadTimeout,
    httpx.RemoteProtocolError,
)


def build_chat_model() -> ChatOpenAI:
    logger.debug("Creating chat model client")
    return ChatOpenAI(
        model=settings.openai_model,
        api_key=SecretStr(settings.openai_api_key),
        base_url=settings.openai_base_url,
        temperature=settings.openai_temperature,
        timeout=settings.llm_call_request_timeout,
    )


def _build_retrying() -> Retrying:
    return Retrying(
        stop=stop_after_attempt(settings.llm_call_retry_attempt),
        wait=wait_exponential(
            multiplier=2, min=settings.llm_call_retry_min_wait, max=settings.llm_call_retry_max_wait
        ),
        retry=retry_if_exception_type(RETRYABLE_LLM_EXCEPTIONS),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True,
    )


def llm_call(call: Callable[[], T]) -> T:
    for attempt in _build_retrying():
        with attempt:
            return call()
    raise RuntimeError("LLM retry loop exited unexpectedly")


def rllm_stream(stream_factory: Callable[[], Iterator[T]]) -> Iterator[T]:
    for attempt in _build_retrying():
        yielded_output = False
        try:
            with attempt:
                for chunk in stream_factory():
                    yielded_output = True
                    yield chunk
                return
        except RETRYABLE_LLM_EXCEPTIONS as err:
            if yielded_output:
                raise

            logger.warning(
                "LLM stream failed after partial output; skipping retry to avoid duplicates"
            )
            raise PartialStreamError(err) from err
