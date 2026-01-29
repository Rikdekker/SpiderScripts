# Error Handling

ADA has a comprehensive exception hierarchy that preserves all error messages and validation from the original Bash version.

## Exception Hierarchy

```
AdaError                          Base exception for all ADA errors
├── AdaConfigError                Configuration missing or invalid
├── AdaSecurityError              File permission violations
├── AdaAuthError                  Authentication setup errors
│   ├── AdaTokenExpiredError      Token expired or about to expire
│   └── AdaTokenPermissionError   Token lacks required permissions
├── AdaAuthenticationError        Server rejected credentials (HTTP 401)
├── AdaAPIError                   dCache API errors (with status_code)
│   ├── AdaNotFoundError          Resource not found (HTTP 404)
│   └── AdaForbiddenError         Access forbidden (HTTP 403)
├── AdaPathError                  Invalid path or path type mismatch
└── AdaValidationError            Input validation errors
```

## Catching Errors

### Library Usage

```python
from ada import AdaClient, AdaError, AdaNotFoundError, AdaTokenExpiredError

try:
    with AdaClient(tokenfile="/path/to/token") as client:
        info = client.stat("/pnfs/data/nonexistent")
except AdaTokenExpiredError as e:
    print(f"Token expired {e.seconds_ago}s ago. Get a new token.")
except AdaNotFoundError:
    print("File not found")
except AdaError as e:
    print(f"ADA error: {e}")
```

### Catch Broad or Specific

```python
# Catch all ADA errors
try:
    client.delete("/pnfs/data/dir", recursive=True)
except AdaError as e:
    handle_error(e)

# Catch specific API errors with status code
try:
    client.stage("/pnfs/data/file.dat")
except AdaAPIError as e:
    print(f"HTTP {e.status_code}: {e.response_body}")
```

### CLI Behavior

The CLI automatically catches all `AdaError` exceptions and prints them to stderr:

```
ERROR: Token has expired 120 seconds ago. tokenfile: /home/user/.ada/token
```

Exit code is `1` for any error.

## Error Categories

### Configuration Errors (`AdaConfigError`)

Raised when the configuration is invalid.

```python
# API URL must start with https://
AdaConfigError("API address must start with 'https://'. Got: http://insecure/api/v1")
```

### Security Errors (`AdaSecurityError`)

Raised when credential files have insecure permissions.

```python
# World-readable token file
AdaSecurityError("File '/home/user/.ada/token' is world readable. Fix with: chmod o-r ...")

# World-writable config
AdaSecurityError("File '/home/user/.ada/ada.conf' is world writable. Fix with: chmod o-w ...")
```

### Authentication Errors (`AdaAuthError`)

Raised during credential setup (before any API calls).

```python
# No auth method specified
AdaAuthError("No authentication method specified. Use --tokenfile, --netrc, or --proxy.")

# Cannot read token file
AdaAuthError("Could not read token from file: /path/to/empty-file")

# Proxy file not found
AdaAuthError("Proxy file not found: /tmp/x509up_u1000")
```

### Token Expired (`AdaTokenExpiredError`)

```python
# Already expired
AdaTokenExpiredError("Token has expired 120 seconds ago. tokenfile: ~/.ada/token",
                     seconds_ago=120)

# About to expire (< 60 seconds remaining)
AdaTokenExpiredError("Token will expire in 30 seconds. Please use a token valid for more than 60 seconds.",
                     seconds_ago=0)
```

### Token Permission Errors (`AdaTokenPermissionError`)

Raised when staging with a token that lacks the required permissions.

```python
# JWT without storage.stage
AdaTokenPermissionError(
    "You want to stage data from tape, but your OIDC token does not have "
    "the storage.stage permission in its scope. "
    "You can check this with the --viewtoken option."
)

# Macaroon without STAGE activity
AdaTokenPermissionError(
    "You want to stage data from tape, but your macaroon token does not have "
    "the STAGE activity permission."
)
```

### API Errors (`AdaAPIError`)

Raised for HTTP error responses from dCache. Includes the status code and response body.

```python
try:
    client.stage("/pnfs/data/dir", recursive=True)
except AdaAPIError as e:
    print(e.status_code)     # 403
    print(e.response_body)   # Raw response from dCache
```

### Staging-Specific Errors (`AdaForbiddenError`)

Detailed error messages for common staging failures:

```python
# Recursive staging prohibited
AdaForbiddenError(
    "Staging failed. Recursive staging may be prohibited by the server. "
    "Try without --recursive. "
    "Ask the system administrators to set 'bulk.allowed-directory-expansion=ALL'."
)

# Directory staging prohibited
AdaForbiddenError(
    "Staging failed. Staging a directory may be prohibited by the server. "
    "Try staging individual files instead."
)
```

### Path Errors (`AdaPathError`)

```python
# Destination already exists
AdaPathError("Target '/pnfs/data/newname' already exists.")

# Directory not empty
AdaPathError("Directory '/pnfs/data/mydir' is not empty (5 items). "
             "Use --recursive to delete it and its contents.")

# Parent doesn't exist
AdaPathError("Parent directory '/pnfs/data/nonexistent' does not exist. "
             "Use --recursive to create it.")

# Labels on directories
AdaPathError("'/pnfs/data/mydir' is a directory. Labels can only be set on files.")
```

### Validation Errors (`AdaValidationError`)

```python
# Too many recursive mkdirs
AdaValidationError("Maximum number of directories that can be created at once is 10.")

# Invalid lifetime
AdaValidationError("Invalid lifetime unit 'X'. Use S (seconds), M (minutes), H (hours), or D (days).")

# Empty file list
AdaValidationError("File list is empty: /path/to/list.txt")
```

## Validation Flow

ADA validates input at multiple levels:

1. **CLI layer**: Click validates argument types and required options
2. **Client layer**: `AdaClient.stage()` validates token permissions before calling the service
3. **Service layer**: Services validate path types, limits, and business rules
4. **HTTP layer**: `DcacheAPI` maps HTTP status codes to appropriate exceptions

This mirrors the Bash version's `validate_input()` function, which checked all inputs before making API calls.
