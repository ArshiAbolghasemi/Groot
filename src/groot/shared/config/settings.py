from dynaconf import Dynaconf

_dynaconf_settings = Dynaconf(
    envvar_prefix=False,
    load_dotenv=True,
    dotenv_override=True,
)


class Settings:
    @property
    def openai_api_key(self) -> str:
        return _dynaconf_settings.get("OPENAI_API_KEY")

    @property
    def openai_base_url(self) -> str:
        return _dynaconf_settings.get("OPENAI_BASE_URL")

    @property
    def openai_model(self) -> str:
        return _dynaconf_settings.get("OPENAI_MODEL")

    @property
    def openai_temperature(self) -> float:
        return float(_dynaconf_settings.get("OPENAI_TEMPERATURE", 0.0))

    @property
    def llm_call_retry_attempt(self) -> int:
        return int(_dynaconf_settings.get("LLM_CALL_RETRY_ATTEMPT", 3))

    @property
    def llm_call_retry_min_wait(self) -> int:
        return int(_dynaconf_settings.get("LLM_CALL_RETRY_MIN_WAIT", 1))

    @property
    def llm_call_retry_max_wait(self) -> int:
        return int(_dynaconf_settings.get("LLM_CALL_RETRY_MAX_WAIT", 10))

    @property
    def llm_call_request_timeout(self) -> int:
        return int(_dynaconf_settings.get("LLM_CALL_REQUEST_TIMEOUT", 30))

    @property
    def database_username(self) -> str:
        return _dynaconf_settings.get("POSTGRES_USER")

    @property
    def database_password(self) -> str:
        return _dynaconf_settings.get("POSTGRES_PASSWORD")

    @property
    def database_host(self) -> str:
        return _dynaconf_settings.get("POSTGRES_HOST", "localhost")

    @property
    def database_port(self) -> int:
        return int(_dynaconf_settings.get("POSTGRES_PORT", 5432))

    @property
    def database_name(self) -> str:
        return _dynaconf_settings.get("POSTGRES_DB")

    @property
    def log_level(self) -> str:
        return _dynaconf_settings.get("LOG_LEVEL", "INFO")

    @property
    def wikipedia_search_url(self) -> str:
        return _dynaconf_settings.get("WIKIPEDIA_SEARCH_URL", "https://en.wikipedia.org/w/api.php")

    @property
    def wikipedia_proxy_url(self) -> str | None:
        return _dynaconf_settings.get("WIKIPEDIA_PROXY_URL")

    @property
    def wikipedia_request_timeout_seconds(self) -> int:
        return int(_dynaconf_settings.get("WIKIPEDIA_REQUEST_TIMEOUT_SECONDS", 30))

    @property
    def wikipedia_reqest_retry_attempt(self) -> int:
        return int(_dynaconf_settings.get("WIKIPEDIA_REQUEST_RETRY_ATTEMPT", 3))

    @property
    def wikipedia_request_retry_min_wait(self) -> int:
        return int(_dynaconf_settings.get("WIKIPEDIA_REQUEST_RETRY_MIN_WAIT", 1))

    @property
    def wikipedia_request_retry_max_wait(self) -> int:
        return int(_dynaconf_settings.get("WIKIPEDIA_REQUEST_RETRY_MAX_WAIT", 10))

    @property
    def wikipedia_search_result_limit(self) -> int:
        return int(_dynaconf_settings.get("WIKIPEDIA_SEARCH_RESULT_LIMIT", 5))

    @property
    def guardrail_prompt(self) -> str:
        return _dynaconf_settings.get(
            "GUARDRAIL_PROMPT",
            """
    You are a strict guardrail classifier.\n\n
    Decide whether the following user question is political.\n\n
    Rules:\n
    - If the question IS political → respond with exactly: {blocked}\n
    - If the question is NOT political → respond with exactly: {allowed}\n\n
    Important:\n
    • Output ONLY a single digit.\n
    • Do NOT output anything else (no explanations, no punctuation).\n\n
    Example:\n
    User question: \"Who should I vote for?\"\n
    Your response: {blocked}\n\n"
        """,
        )

    @property
    def guardrail_blocked_messae(self) -> str:
        return _dynaconf_settings.get(
            "GUARDRAIL_BLOCKED_MESSAGE",
            """
    I'm sorry, I'm not able to discuss political topics.
    Please ask me something else I can help you with.
            """,
        )

    @property
    def system_prompt(self) -> str:
        return _dynaconf_settings.get(
            "SYSTEM_PROMPT",
            """
            """,
        )


settings = Settings()
