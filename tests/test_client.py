"""Tests for FLLClient."""

import pytest
from unittest.mock import patch, MagicMock

from fll_sdk import FLLClient
from fll_sdk.exceptions import AuthError, ApiError, NotFoundError
from fll_sdk.models import Baby, Task, Achievement, Notification, Webhook


class TestFLLClient:
    """Test cases for FLLClient."""

    @patch('fll_sdk.auth.requests.post')
    def test_login_success(self, mock_post):
        """Test successful login returns token."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'token': 'test-jwt-token'}
        mock_post.return_value = mock_response

        client = FLLClient(api_key='key', api_secret='secret')
        token = client.login()

        assert token == 'test-jwt-token'
        assert client._auth.token == 'test-jwt-token'

    @patch('fll_sdk.auth.requests.post')
    def test_login_failure(self, mock_post):
        """Test login with invalid credentials raises AuthError."""
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_post.return_value = mock_response

        client = FLLClient(api_key='bad', api_secret='keys')

        with pytest.raises(AuthError):
            client.login()

    def test_init_without_credentials(self):
        """Test client can be initialized without credentials."""
        client = FLLClient()
        assert client.api_key is None
        assert client.api_secret is None

    def test_init_with_token(self):
        """Test client can be initialized with pre-existing token."""
        client = FLLClient(token='pre-existing-token')
        assert client._auth.token == 'pre-existing-token'

    @patch('fll_sdk.client.requests.request')
    @patch('fll_sdk.auth.requests.post')
    def test_babies_list(self, mock_auth_post, mock_request):
        """Test listing babies."""
        # Setup auth
        mock_auth_response = MagicMock()
        mock_auth_response.status_code = 200
        mock_auth_response.json.return_value = {'token': 'test-token'}
        mock_auth_post.return_value = mock_auth_response

        # Setup babies response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b'[{ "id": "b1", "name": "Test Baby", "gender": "male", "birthdate": "2020-01-01" }]'
        mock_response.json.return_value = [{'id': 'b1', 'name': 'Test Baby', 'gender': 'male', 'birthdate': '2020-01-01'}]
        mock_request.return_value = mock_response

        client = FLLClient(api_key='key', api_secret='secret')
        client.login()
        babies = client.babies.list()

        assert len(babies) == 1
        assert babies[0].id == 'b1'
        assert babies[0].name == 'Test Baby'

    @patch('fll_sdk.client.requests.request')
    @patch('fll_sdk.auth.requests.post')
    def test_tasks_create(self, mock_auth_post, mock_request):
        """Test creating a task."""
        # Setup auth
        mock_auth_response = MagicMock()
        mock_auth_response.status_code = 200
        mock_auth_response.json.return_value = {'token': 'test-token'}
        mock_auth_post.return_value = mock_auth_response

        # Setup task creation response
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            'id': 'task-1',
            'baby_id': 'b1',
            'title': 'Test Task',
            'points': 10,
            'type': 'checkin',
            'tags': [],
            'status': 'ongoing',
            'completed': 0,
            'total': 1,
            'created_at': '2026-05-18T00:00:00Z',
            'updated_at': '2026-05-18T00:00:00Z',
        }
        mock_request.return_value = mock_response

        client = FLLClient(api_key='key', api_secret='secret')
        client.login()
        task = client.tasks.create(baby_id='b1', title='Test Task', points=10)

        assert task.id == 'task-1'
        assert task.title == 'Test Task'
        assert task.points == 10

    @patch('fll_sdk.client.requests.request')
    @patch('fll_sdk.auth.requests.post')
    def test_tasks_complete(self, mock_auth_post, mock_request):
        """Test completing a task."""
        # Setup auth
        mock_auth_response = MagicMock()
        mock_auth_response.status_code = 200
        mock_auth_response.json.return_value = {'token': 'test-token'}
        mock_auth_post.return_value = mock_auth_response

        # Setup complete response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'success': True, 'task_id': 'task-1'}
        mock_request.return_value = mock_response

        client = FLLClient(api_key='key', api_secret='secret')
        client.login()
        result = client.tasks.complete('task-1')

        assert result['success'] is True

    @patch('fll_sdk.client.requests.request')
    @patch('fll_sdk.auth.requests.post')
    def test_not_found_error(self, mock_auth_post, mock_request):
        """Test 404 returns NotFoundError."""
        # Setup auth
        mock_auth_response = MagicMock()
        mock_auth_response.status_code = 200
        mock_auth_response.json.return_value = {'token': 'test-token'}
        mock_auth_post.return_value = mock_auth_response

        # Setup 404 response
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = 'Not found'
        mock_request.return_value = mock_response

        client = FLLClient(api_key='key', api_secret='secret')
        client.login()

        with pytest.raises(NotFoundError):
            client.babies.get('nonexistent-id')


class TestModels:
    """Test Pydantic models."""

    def test_baby_model(self):
        """Test Baby model validation."""
        baby = Baby(
            id='b1',
            name='Test',
            gender='male',
            birthdate='2020-01-01'
        )
        assert baby.id == 'b1'
        assert baby.name == 'Test'

    def test_task_model(self):
        """Test Task model validation."""
        task = Task(
            id='t1',
            baby_id='b1',
            title='Test Task',
            type='checkin',
            status='ongoing',
            points=10,
            created_at='2026-05-18T00:00:00Z',
            updated_at='2026-05-18T00:00:00Z',
        )
        assert task.title == 'Test Task'
        assert task.type == 'checkin'

    def test_webhook_model(self):
        """Test Webhook model."""
        webhook = Webhook(
            id='wh1',
            url='https://example.com/webhook',
            events=['task.completed'],
            secret='secret123',
            active=True
        )
        assert webhook.url == 'https://example.com/webhook'
        assert 'task.completed' in webhook.events


class TestWebhookSignature:
    """Test webhook signature verification."""

    def test_verify_signature(self):
        """Test signature verification."""
        from fll_sdk.webhooks import verify_signature
        import hmac
        import hashlib

        secret = 'test-secret'
        payload = b'{"event": "test"}'
        signature = 'sha256=' + hmac.new(
            secret.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()

        assert verify_signature(payload, signature, secret) is True

    def test_verify_signature_invalid(self):
        """Test invalid signature is rejected."""
        from fll_sdk.webhooks import verify_signature

        secret = 'test-secret'
        payload = b'{"event": "test"}'
        wrong_signature = 'sha256=invalid'

        assert verify_signature(payload, wrong_signature, secret) is False

    def test_verify_signature_wrong_prefix(self):
        """Test signature without sha256= prefix is rejected."""
        from fll_sdk.webhooks import verify_signature

        secret = 'test-secret'
        payload = b'{"event": "test"}'
        wrong_format = 'md5=abcdef'

        assert verify_signature(payload, wrong_format, secret) is False