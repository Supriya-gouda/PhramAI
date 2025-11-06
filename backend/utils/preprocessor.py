"""Text preprocessing utilities."""


def preprocess_text(text: str) -> str:
    """Simple placeholder preprocessor: strip and collapse whitespace."""
    if text is None:
        return ""
    return " ".join(str(text).split())
