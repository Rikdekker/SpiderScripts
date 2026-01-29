"""Token validation logic.

Validates JWT and Macaroon tokens for expiry and required permissions,
replicating the Bash ``check_token`` function.
"""

from __future__ import annotations

import logging
import time
from typing import Optional

from ada.exceptions import AdaAuthError, AdaTokenExpiredError, AdaTokenPermissionError
from ada.tokens.jwt import decode_jwt_payload, get_jwt_expiry, get_jwt_scope, is_jwt
from ada.tokens.macaroon import decode_macaroon_raw, extract_macaroon_expiry

logger = logging.getLogger("ada.tokens")

MIN_VALID_TIME = 60  # seconds — token must be valid for at least this long


def validate_token(
    token: str, source: str = "", command: Optional[str] = None
) -> None:
    """Validate a token (JWT or Macaroon) for expiry and permissions.

    Args:
        token: The raw token string.
        source: Description of where the token came from (for error messages).
        command: The command being executed (e.g., "stage"), used to check
            command-specific permissions.

    Raises:
        AdaTokenExpiredError: If the token has expired or is about to expire.
        AdaTokenPermissionError: If the token lacks required permissions.
        AdaAuthError: If the token cannot be decoded.
    """
    if is_jwt(token):
        _validate_jwt(token, source, command)
    else:
        _validate_macaroon(token, source, command)


def _validate_jwt(token: str, source: str, command: Optional[str]) -> None:
    """Validate a JWT/OIDC token."""
    exp_unix = get_jwt_expiry(token)
    _check_expiry(exp_unix, source)

    if command == "stage":
        scope = get_jwt_scope(token)
        # Only check if there are storage.* claims at all.
        # If no storage.* claims, dCache assumes everything is allowed.
        if "storage." in scope and "storage.stage" not in scope:
            raise AdaTokenPermissionError(
                "You want to stage data from tape, but your OIDC token "
                "does not have the storage.stage permission in its scope. "
                "You can check this with the --viewtoken option. "
                "Please use an OIDC token with 'storage.stage' in its scope."
            )


def _validate_macaroon(token: str, source: str, command: Optional[str]) -> None:
    """Validate a Macaroon token."""
    decoded = decode_macaroon_raw(token)
    exp_unix = extract_macaroon_expiry(decoded)
    _check_expiry(exp_unix, source)

    if command == "stage":
        # Check for STAGE activity permission
        if "activity:" in decoded and "STAGE" not in decoded:
            raise AdaTokenPermissionError(
                "You want to stage data from tape, but your macaroon token "
                "does not have the STAGE activity permission. "
                "You can check this with the --viewtoken option. "
                "Please use a macaroon with the STAGE activity permission."
            )


def _check_expiry(exp_unix: Optional[int], source: str) -> None:
    """Check token expiration timestamp.

    Raises:
        AdaAuthError: If expiration field is missing or invalid.
        AdaTokenExpiredError: If the token has expired or will expire soon.
    """
    if exp_unix is None or not isinstance(exp_unix, (int, float)):
        raise AdaAuthError(
            f"Invalid token: missing or invalid expiration field. {source}"
        )

    now = int(time.time())

    if now >= exp_unix:
        raise AdaTokenExpiredError(
            f"Token has expired {now - exp_unix} seconds ago. {source}",
            seconds_ago=now - exp_unix,
        )

    if now >= exp_unix - MIN_VALID_TIME:
        raise AdaTokenExpiredError(
            f"Token will expire in {exp_unix - now} seconds. "
            f"Please use a token that is valid for more than {MIN_VALID_TIME} seconds, "
            f"to ensure Ada can finish the task. {source}",
            seconds_ago=0,
        )
