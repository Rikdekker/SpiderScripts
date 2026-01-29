"""ADA - Advanced dCache API tool."""

from ada.core.client import AdaClient
from ada.exceptions import (
    AdaAPIError,
    AdaAuthenticationError,
    AdaAuthError,
    AdaConfigError,
    AdaError,
    AdaForbiddenError,
    AdaNotFoundError,
    AdaPathError,
    AdaSecurityError,
    AdaTokenExpiredError,
    AdaTokenPermissionError,
    AdaValidationError,
)

try:
    from importlib.metadata import version

    __version__ = version("ada-dcache")
except Exception:
    __version__ = "0.0.0-dev"

__all__ = [
    "AdaClient",
    "AdaAPIError",
    "AdaAuthError",
    "AdaAuthenticationError",
    "AdaConfigError",
    "AdaError",
    "AdaForbiddenError",
    "AdaNotFoundError",
    "AdaPathError",
    "AdaSecurityError",
    "AdaTokenExpiredError",
    "AdaTokenPermissionError",
    "AdaValidationError",
]
