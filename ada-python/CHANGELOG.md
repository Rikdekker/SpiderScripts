# Changelog

## [0.1.1] - 2025-01-30

### Fixed

- **Netrc authentication**: `auth` parameter was never passed to httpx requests,
  making `--netrc` non-functional. Also fixed `NetrcAuth.get_httpx_auth()` to
  return `httpx.BasicAuth` instead of a raw `netrc` object, and to look up
  credentials for the correct API hostname.
- **URL encoding of paths**: `encode_path()` now encodes all characters
  including `/` (matching the Bash `jq -sRr @uri` behavior). Previously slashes
  were kept literal, producing malformed URLs like
  `.../namespace//pnfs/data/...` instead of `.../namespace/%2Fpnfs%2Fdata%2F...`.
- **Token whitespace**: Bearer tokens are now stripped on read, preventing
  trailing whitespace or newlines from breaking the `Authorization` header.

### Improved

- **Installation docs**: Added virtual environment setup steps to README and
  getting-started guide (required on macOS with PEP 668).
- **PATH conflict guidance**: Added `which ada` verification tip to detect
  conflicts with the older Bash version of ada.
- **Debug logging**: Token type detection (JWT/OIDC vs Macaroon) is now logged
  at debug level for easier troubleshooting.

## [0.1.0] - 2025-01-29

### Added

- Initial Python implementation of ADA (Advanced dCache API).
- Full CLI with 25+ commands: namespace, labels, xattr, staging, events,
  checksums, and system info.
- Three authentication methods: Bearer token (JWT/OIDC and Macaroon), netrc,
  and X.509 proxy certificates.
- Usable as both a CLI tool (`ada`) and a Python library (`AdaClient`).
- Configuration via files (`~/.ada/ada.conf`), environment variables, and
  CLI arguments.
- Token validation with expiry checks and permission verification.
- File permission security checks on token and netrc files.
- SSE streaming support for dCache events.
- Comprehensive documentation and unit tests.
