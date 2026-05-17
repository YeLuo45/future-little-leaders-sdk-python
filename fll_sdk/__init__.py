"""Future Little Leaders Python SDK."""

__version__ = '1.0.0'

from fll_sdk.client import FLLClient
from fll_sdk.exceptions import SDKError, AuthError, ApiError, NotFoundError

__all__ = [
    '__version__',
    'FLLClient',
    'SDKError',
    'AuthError',
    'ApiError',
    'NotFoundError',
]