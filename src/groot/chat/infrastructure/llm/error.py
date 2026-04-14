class PartialStreamError(Exception):
    """Raised after partial stream output to prevent retrying and sending duplicates."""

    cause: BaseException

    def __init__(self, cause: BaseException) -> None:
        self.cause = cause
        super().__init__(str(cause))
