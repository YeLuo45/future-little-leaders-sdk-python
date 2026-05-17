"""Custom exceptions for fll_sdk."""


class SDKError(Exception):
    """Base exception for all SDK errors."""
    pass


class AuthError(SDKError):
    """Authentication failed (invalid credentials, expired token, etc.)."""
    pass


class ApiError(SDKError):
    """API request failed (non-2xx response, network error, etc.)."""

    def __init__(self, message: str, status_code: int = None, response_body: str = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body


class NotFoundError(ApiError):
    """Resource not found (404)."""

    def __init__(self, message: str = 'Resource not found', status_code: int = 404, response_body: str = None):
        super().__init__(message, status_code, response_body)