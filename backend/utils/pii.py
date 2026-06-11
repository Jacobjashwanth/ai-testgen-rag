import re
from dataclasses import dataclass

# ---------------------------------------------------------------------------
# PII patterns
# ---------------------------------------------------------------------------
PII_PATTERNS = {
    "email":       r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}",
    "phone":       r"(\+?1[\s\-.]?)?\(?\d{3}\)?[\s\-.]?\d{3}[\s\-.]?\d{4}",
    "ssn":         r"\b\d{3}[-\s]?\d{2}[-\s]?\d{4}\b",
    "credit_card": r"\b(?:\d[ \-]?){13,16}\b",
    "api_key":     r"(sk|pk|api|key|token|secret)[_\-]?[a-zA-Z0-9]{16,}",
    "ip_address":  r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
    "aws_key":     r"AKIA[0-9A-Z]{16}",
}

MASK_MAP = {
    "email":       "[EMAIL]",
    "phone":       "[PHONE]",
    "ssn":         "[SSN]",
    "credit_card": "[CARD]",
    "api_key":     "[API_KEY]",
    "ip_address":  "[IP]",
    "aws_key":     "[AWS_KEY]",
}


@dataclass
class PIIDetectionResult:
    has_pii: bool
    findings: dict[str, int]   # pii_type -> count
    summary: str


def detect_pii(text: str) -> PIIDetectionResult:
    """Scan text for PII and return a detection result."""
    findings = {}
    for pii_type, pattern in PII_PATTERNS.items():
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            findings[pii_type] = len(matches)

    has_pii = bool(findings)
    if findings:
        parts = [f"{count} {pii_type}(s)" for pii_type, count in findings.items()]
        summary = "PII detected: " + ", ".join(parts)
    else:
        summary = "No PII detected"

    return PIIDetectionResult(has_pii=has_pii, findings=findings, summary=summary)


def mask_pii(text: str) -> str:
    """Replace all PII in text with masked placeholders."""
    masked = text
    for pii_type, pattern in PII_PATTERNS.items():
        masked = re.sub(pattern, MASK_MAP[pii_type], masked, flags=re.IGNORECASE)
    return masked


def scrub_prompt(prompt: str) -> str:
    """Scrub PII from a prompt before sending to LLM."""
    return mask_pii(prompt)


def scrub_log_message(message: str) -> str:
    """Scrub PII from log messages."""
    return mask_pii(message)


def scrub_code_for_llm(code: str) -> str:
    """
    Scrub PII from code context before sending to external LLM (Claude API).
    For local Ollama, scrubbing is optional but still good practice.
    """
    return mask_pii(code)