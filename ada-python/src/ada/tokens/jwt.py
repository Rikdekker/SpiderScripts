"""JWT/OIDC token handling.

Decodes and inspects JWT tokens without requiring external libraries
by using base64 decoding of the payload section.
"""

from __future__ import annotations

import base64
import json
import re
from datetime import datetime, timezone
from typing import Any, Optional

from ada.exceptions import AdaAuthError

# JWT pattern: three base64url-encoded parts separated by dots
JWT_PATTERN = re.compile(r"^[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+$")


def is_jwt(token: str) -> bool:
    """Check if a token looks like a JWT (three dot-separated base64url parts)."""
    return bool(JWT_PATTERN.match(token.strip()))


def decode_jwt_payload(token: str) -> dict[str, Any]:
    """Decode the payload section of a JWT token.

    Does NOT verify the signature — this is for inspection only,
    matching the Bash version's behavior.

    Returns:
        Decoded payload as a dict.

    Raises:
        AdaAuthError: If the token cannot be decoded.
    """
    parts = token.strip().split(".")
    if len(parts) != 3:
        raise AdaAuthError("Invalid JWT: expected 3 dot-separated parts")

    payload_b64 = parts[1]
    # Add padding if needed (base64url omits trailing =)
    padding = 4 - len(payload_b64) % 4
    if padding != 4:
        payload_b64 += "=" * padding

    try:
        payload_bytes = base64.urlsafe_b64decode(payload_b64)
        return json.loads(payload_bytes)
    except Exception as exc:
        raise AdaAuthError(f"Invalid JWT: cannot decode payload: {exc}") from exc


def decode_jwt(token: str) -> dict[str, Any]:
    """Decode a JWT and return payload with human-readable timestamps.

    Converts ``exp``, ``nbf``, and ``iat`` fields from Unix timestamps
    to ISO 8601 strings (matching the Bash ``jq .exp |= todate`` behavior).
    """
    payload = decode_jwt_payload(token)
    result = dict(payload)
    for field in ("exp", "nbf", "iat"):
        if field in result and isinstance(result[field], (int, float)):
            try:
                result[field] = datetime.fromtimestamp(
                    result[field], tz=timezone.utc
                ).isoformat()
            except (OSError, ValueError):
                pass  # Keep original value if conversion fails
    return result


def get_jwt_expiry(token: str) -> Optional[int]:
    """Extract the expiration timestamp (exp) from a JWT.

    Returns:
        Unix timestamp as int, or None if not present.
    """
    payload = decode_jwt_payload(token)
    exp = payload.get("exp")
    if isinstance(exp, (int, float)):
        return int(exp)
    return None


def get_jwt_scope(token: str) -> str:
    """Extract the scope claim from a JWT.

    Returns:
        The scope string, or empty string if not present.
    """
    payload = decode_jwt_payload(token)
    return str(payload.get("scope", ""))
