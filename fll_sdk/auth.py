"""JWT authentication helpers for fll_sdk."""

import time
from typing import Optional

import jwt
import requests

from fll_sdk.exceptions import AuthError


class Auth:
    """Handles JWT token acquisition and refresh."""

    def __init__(self, api_key: str, api_secret: str, base_url: str):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url.rstrip('/')
        self._token: Optional[str] = None
        self._token_expires_at: int = 0

    def login(self) -> str:
        """Authenticate with API key + secret and get JWT token."""
        try:
            response = requests.post(
                f'{self.base_url}/api/v1/auth/login',
                json={
                    'api_key': self.api_key,
                    'api_secret': self.api_secret,
                },
                timeout=30,
            )
            if response.status_code == 401:
                raise AuthError('Invalid API credentials')
            response.raise_for_status()
            data = response.json()
            self._token = data['token']
            # JWT payload: decode without verification to get exp (for informational use)
            try:
                payload = jwt.decode(self._token, options={'verify_signature': False})
                self._token_expires_at = payload.get('exp', 0)
            except Exception:
                # Set a default expiration if we can't decode
                self._token_expires_at = int(time.time()) + 86400
            return self._token
        except requests.RequestException as e:
            raise AuthError(f'Authentication request failed: {e}')

    def refresh_token(self) -> str:
        """Refresh the JWT token."""
        return self.login()

    @property
    def token(self) -> Optional[str]:
        """Current JWT token."""
        return self._token

    @property
    def is_token_expired(self) -> bool:
        """Check if current token is expired or about to expire (within 60s)."""
        if not self._token:
            return True
        return int(time.time()) >= (self._token_expires_at - 60)

    def ensure_valid_token(self) -> str:
        """Ensure we have a valid token, refreshing if necessary."""
        if self.is_token_expired or not self._token:
            return self.login()
        return self._token