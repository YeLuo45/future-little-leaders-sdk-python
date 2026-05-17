"""FLLClient - main API client for Future Little Leaders SDK."""

import requests
from typing import Optional, Callable, List

from fll_sdk.auth import Auth
from fll_sdk.exceptions import ApiError, NotFoundError
from fll_sdk.models import Baby, Task, Achievement, Notification, Webhook


class BabiesEndpoint:
    """API methods for /babies."""

    def __init__(self, client: 'FLLClient'):
        self._client = client

    def list(self) -> List[Baby]:
        """Get all babies/children."""
        resp = self._client._request('GET', '/api/v1/babies')
        return [Baby(**item) for item in resp]

    def get(self, baby_id: str) -> Baby:
        """Get a baby by ID."""
        try:
            resp = self._client._request('GET', f'/api/v1/babies/{baby_id}')
            return Baby(**resp)
        except ApiError as e:
            if e.status_code == 404:
                raise NotFoundError(f'Baby not found: {baby_id}', status_code=404)
            raise

    def create(self, name: str, birthdate: str, gender: str, avatar: str = None) -> Baby:
        """Create a new baby/child record."""
        payload = {'name': name, 'birthdate': birthdate, 'gender': gender}
        if avatar:
            payload['avatar'] = avatar
        resp = self._client._request('POST', '/api/v1/babies', json=payload)
        return Baby(**resp)


class TasksEndpoint:
    """API methods for /tasks."""

    def __init__(self, client: 'FLLClient'):
        self._client = client

    def list(self, baby_id: str = None, status: str = None) -> List[Task]:
        """List tasks, optionally filtered by baby_id and/or status."""
        params = {}
        if baby_id:
            params['baby_id'] = baby_id
        if status:
            params['status'] = status
        resp = self._client._request('GET', '/api/v1/tasks', params=params)
        return [Task(**item) for item in resp]

    def create(
        self,
        baby_id: str,
        title: str,
        points: int = 0,
        type: str = 'checkin',
        tags: List[str] = None,
        description: str = None,
        **kwargs
    ) -> Task:
        """Create a new task."""
        payload = {
            'baby_id': baby_id,
            'title': title,
            'points': points,
            'type': type,
        }
        if tags:
            payload['tags'] = tags
        if description:
            payload['description'] = description
        payload.update(kwargs)
        resp = self._client._request('POST', '/api/v1/tasks', json=payload)
        return Task(**resp)

    def complete(self, task_id: str) -> dict:
        """Mark a task as completed."""
        resp = self._client._request('POST', f'/api/v1/tasks/{task_id}/complete')
        return resp

    def update(self, task_id: str, **kwargs) -> Task:
        """Update a task."""
        resp = self._client._request('PUT', f'/api/v1/tasks/{task_id}', json=kwargs)
        return Task(**resp)


class AchievementsEndpoint:
    """API methods for /achievements."""

    def __init__(self, client: 'FLLClient'):
        self._client = client

    def list(self, baby_id: str = None) -> List[Achievement]:
        """List achievements, optionally filtered by baby_id."""
        params = {}
        if baby_id:
            params['baby_id'] = baby_id
        resp = self._client._request('GET', '/api/v1/achievements', params=params)
        return [Achievement(**item) for item in resp]

    def unlock(self, baby_id: str, achievement_id: str) -> Achievement:
        """Unlock an achievement for a baby."""
        resp = self._client._request(
            'POST',
            '/api/v1/achievements/unlock',
            json={'baby_id': baby_id, 'achievement_id': achievement_id}
        )
        return Achievement(**resp)


class NotificationsEndpoint:
    """API methods for /notifications."""

    def __init__(self, client: 'FLLClient'):
        self._client = client

    def list(self, baby_id: str = None, channel: str = None) -> List[Notification]:
        """List notifications."""
        params = {}
        if baby_id:
            params['baby_id'] = baby_id
        if channel:
            params['channel'] = channel
        resp = self._client._request('GET', '/api/v1/notifications', params=params)
        return [Notification(**item) for item in resp]

    def mark_read(self, notification_ids: List[str]) -> dict:
        """Mark notifications as read."""
        resp = self._client._request(
            'POST',
            '/api/v1/notifications/read',
            json={'notification_ids': notification_ids}
        )
        return resp


class PointsEndpoint:
    """API methods for /points."""

    def __init__(self, client: 'FLLClient'):
        self._client = client

    def balance(self, baby_id: str) -> int:
        """Get points balance for a baby."""
        resp = self._client._request('GET', '/api/v1/points/balance', params={'baby_id': baby_id})
        return resp.get('balance', 0)

    def award(self, baby_id: str, points: int, reason: str) -> dict:
        """Award points to a baby."""
        resp = self._client._request(
            'POST',
            '/api/v1/points/award',
            json={'baby_id': baby_id, 'points': points, 'reason': reason}
        )
        return resp


class WebhooksEndpoint:
    """API methods for /webhooks."""

    def __init__(self, client: 'FLLClient'):
        self._client = client

    def subscribe(self, event: str, url: str) -> Webhook:
        """Subscribe to a webhook event."""
        resp = self._client._request(
            'POST',
            '/api/v1/webhooks/subscribe',
            json={'event': event, 'url': url}
        )
        return Webhook(**resp)

    def list(self) -> List[Webhook]:
        """List all webhook subscriptions."""
        resp = self._client._request('GET', '/api/v1/webhooks')
        return [Webhook(**item) for item in resp]

    def delete(self, webhook_id: str) -> dict:
        """Delete a webhook subscription."""
        resp = self._client._request('DELETE', f'/api/v1/webhooks/{webhook_id}')
        return resp


class FLLClient:
    """
    Main client for Future Little Leaders API.

    Example usage:
        client = FLLClient(api_key='your-key', api_secret='your-secret')
        client.login()

        babies = client.babies.list()
        task = client.tasks.create(baby_id='...', title='Morning Check-in', points=10)
        client.tasks.complete(task.id)
    """

    def __init__(
        self,
        api_key: str = None,
        api_secret: str = None,
        base_url: str = 'https://api.futurelittleleaders.example',
        token: str = None,
    ):
        """
        Initialize the FLL client.

        Args:
            api_key: API key for authentication.
            api_secret: API secret for authentication.
            base_url: Base URL of the API server.
            token: Pre-existing JWT token (skip login if provided).
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url.rstrip('/')

        # Initialize auth handler
        if token:
            self._auth = Auth(api_key or '', api_secret or '', base_url)
            self._auth._token = token
        else:
            self._auth = Auth(api_key or '', api_secret or '', base_url)

        # Endpoint groups
        self.babies = BabiesEndpoint(self)
        self.tasks = TasksEndpoint(self)
        self.achievements = AchievementsEndpoint(self)
        self.notifications = NotificationsEndpoint(self)
        self.points = PointsEndpoint(self)
        self.webhooks = WebhooksEndpoint(self)

    def login(self) -> str:
        """
        Authenticate and obtain JWT token.

        Returns:
            JWT token string.

        Raises:
            AuthError: If authentication fails.
        """
        return self._auth.login()

    def refresh_token(self) -> str:
        """Refresh the JWT token."""
        return self._auth.refresh_token()

    def _request(
        self,
        method: str,
        path: str,
        params: dict = None,
        json: dict = None,
    ) -> dict:
        """
        Make an authenticated API request.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.).
            path: API endpoint path.
            params: Query parameters.
            json: JSON body.

        Returns:
            Parsed JSON response.

        Raises:
            ApiError: On request failure.
            NotFoundError: On 404 response.
        """
        url = f'{self.base_url}{path}'
        headers = {}

        # Ensure we have a valid token
        if self._auth.token is None:
            self._auth.ensure_valid_token()

        if self._auth.token:
            headers['Authorization'] = f'Bearer {self._auth.token}'

        try:
            response = requests.request(
                method,
                url,
                headers=headers,
                params=params,
                json=json,
                timeout=30,
            )

            if response.status_code == 404:
                raise NotFoundError(
                    f'Resource not found: {path}',
                    status_code=404,
                    response_body=response.text,
                )
            if response.status_code >= 400:
                raise ApiError(
                    f'API request failed: {response.status_code}',
                    status_code=response.status_code,
                    response_body=response.text,
                )

            if response.content:
                return response.json()
            return {}
        except requests.RequestException as e:
            raise ApiError(f'Request failed: {e}')