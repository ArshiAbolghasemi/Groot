class OrchestrationError(Exception):
    """Raised when orchestraion workflow has a problem."""


class GuardrailInvalidResponseError(Exception):
    """Raised when guardrail model responds with anything other than 0 or 1."""
