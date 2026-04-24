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
    def wikipedia_user_agent(self) -> str:
        return _dynaconf_settings.get(
            "WIKIPEDIA_USER_AGENT", "Groot/1.0 (arshiabolghasemi@gmail.com)"
        )

    @property
    def guardrail_prompt(self) -> str:
        return _dynaconf_settings.get(
            "GUARDRAIL_PROMPT",
            """
You are a strict guardrail classifier.
Decide whether the following user question is political.

Rules:
- If the question IS political → respond with exactly: {blocked}
- If the question is NOT political → respond with exactly: {allowed}

Important:
• Output ONLY a single digit.
• Do NOT output anything else (no explanations, no punctuation).

Example:
User question: \"Who should I vote for?\"
Your response: {blocked}"
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
    def ner_prompt(self) -> str:
        return _dynaconf_settings.get(
            "NER_PROMPT",
            """
You are a Named Entity Recognition (NER) system.
Extract all named entities from the user's question.

Return a JSON array of objects with the following structure:
[
    {{"entity": "entity text", "type": "PERSON|LOCATION|ORGANIZATION|DATE|OTHER"}}
]

Rules:
- Extract only clear, specific named entities
- Classify each entity into one of: PERSON, LOCATION, ORGANIZATION, DATE, OTHER
- Return ONLY valid JSON, no explanations
- If no entities found, return empty array: []

Examples:
Question: "Who is Albert Einstein?"
Response: [{{"entity": "Albert Einstein", "type": "PERSON"}}]

Question: "What is the capital of France?"
Response: [{{"entity": "France", "type": "LOCATION"}}]

Question: "Tell me about Microsoft"
Response: [{{"entity": "Microsoft", "type": "ORGANIZATION"}}]
    """,
        )

    @property
    def agent_prompt(self) -> str:
        return _dynaconf_settings.get(
            "AGENT_PROMPT",
            """
You are a helpful, intelligent assistant.

Your job is to answer user questions clearly, accurately, and step-by-step when needed.

Guidelines:
- Understand the user’s intent before answering.
- Keep explanations simple and structured.
- If the question is complex, break it into steps.
- Use examples when they help understanding.
- Prefer practical explanations over abstract theory.
- If code is relevant, provide clean and minimal examples.
- If something is uncertain, clearly state assumptions.
- Do not over-explain or add unnecessary information.
- If the user asks for clarification, simplify your answer further.

Always aim to be:
- Correct
- Concise
- Useful in practice
            """,
        )


settings = Settings()
