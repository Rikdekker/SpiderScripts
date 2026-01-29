"""Macaroon token handling.

Decodes Macaroon tokens using base64 decoding and text parsing,
matching the Bash version's approach.
"""

from __future__ import annotations

import base64
import re
from datetime import datetime, timezone
from typing import Optional

from ada.exceptions import AdaAuthError


def is_macaroon(token: str) -> bool:
    """Check if a token looks like a Macaroon (not a JWT)."""
    from ada.tokens.jwt import is_jwt

    return not is_jwt(token)


def decode_macaroon_raw(token: str) -> str:
    """Decode a Macaroon token to its raw text representation.

    Replicates the Bash decoding logic:
        base64 -d | awk '{print substr($0, 5)}' | grep -v 'signature' | tr -d '\\0'

    Returns:
        Decoded macaroon text (caveats, etc.).

    Raises:
        AdaAuthError: If the token cannot be decoded.
    """
    try:
        decoded_bytes = base64.b64decode(token.strip())
    except Exception as exc:
        raise AdaAuthError(f"Invalid macaroon: cannot base64 decode: {exc}") from exc

    # Strip first 4 bytes (binary header), remove null bytes,
    # filter out signature lines
    try:
        text = decoded_bytes[4:].decode("utf-8", errors="replace")
        text = text.replace("\0", "")
        lines = [
            line for line in text.splitlines() if "signature" not in line.lower()
        ]
        result = "\n".join(lines).strip()
    except Exception as exc:
        raise AdaAuthError(f"Invalid macaroon: cannot decode content: {exc}") from exc

    if not result:
        raise AdaAuthError("Invalid macaroon: empty after decoding")

    return result


def decode_macaroon(token: str) -> dict[str, str]:
    """Decode a Macaroon and return its properties as a dict.

    Parses the decoded text for known fields like ``before:``,
    ``activity:``, ``path:``, ``id:``, etc.
    """
    raw = decode_macaroon_raw(token)
    properties: dict[str, str] = {"raw": raw}

    # Extract common Macaroon caveats
    for line in raw.splitlines():
        line = line.strip()
        if ":" in line:
            key, _, value = line.partition(":")
            key = key.strip().lower()
            if key in ("before", "activity", "path", "id", "ip", "home", "root"):
                properties[key] = value.strip()

    return properties


def extract_macaroon_expiry(decoded_text: str) -> Optional[int]:
    """Extract the expiration timestamp from decoded Macaroon text.

    Looks for ``before:`` caveat with ISO 8601 timestamp.

    Returns:
        Unix timestamp as int, or None if not found.
    """
    match = re.search(r"before:([0-9T:.\-]+Z)", decoded_text)
    if not match:
        return None

    exp_str = match.group(1)
    try:
        # Parse ISO 8601 timestamp (e.g., "2024-12-31T23:59:59.000Z")
        # Try with microseconds first, then without
        for fmt in ("%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S"):
            try:
                dt = datetime.strptime(exp_str[:26], fmt)
                dt = dt.replace(tzinfo=timezone.utc)
                return int(dt.timestamp())
            except ValueError:
                continue
        # Fallback: try parsing just the first 19 chars
        dt = datetime.strptime(exp_str[:19], "%Y-%m-%dT%H:%M:%S")
        dt = dt.replace(tzinfo=timezone.utc)
        return int(dt.timestamp())
    except (ValueError, OSError) as exc:
        raise AdaAuthError(
            f"Invalid macaroon: unable to parse 'before' timestamp: {exp_str}"
        ) from exc
