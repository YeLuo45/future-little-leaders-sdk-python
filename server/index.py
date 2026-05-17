#!/usr/bin/env python3
"""
Cloudflare Worker entry point for Future Little Leaders API.

This is a placeholder implementation demonstrating how the API
would be deployed as a Cloudflare Worker.

In production, this would use:
- Cloudflare Workers KV for storage
- Cloudflare D1 for relational data
- JWT verification via crypto.verify()
"""

from typing import Tuple


class Request:
    def __init__(self, method: str, path: str, headers: dict = None, body: bytes = None):
        self.method = method
        self.path = path
        self.headers = headers or {}
        self.body = body or b''


class Response:
    def __init__(self, status: int = 200, body: str = '', headers: dict = None):
        self.status = status
        self.body = body
        self.headers = headers or {'Content-Type': 'application/json'}


def handle_auth_login(request: Request) -> Response:
    """Handle POST /api/v1/auth/login"""
    # Placeholder: In production, verify api_key + api_secret against KV store
    # and return a signed JWT
    return Response(
        status=200,
        body='{"token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.placeholder"}'
    )


def handle_babies_list(request: Request) -> Response:
    """Handle GET /api/v1/babies"""
    # Placeholder: Return empty list
    return Response(status=200, body='[]')


def handle_tasks_list(request: Request) -> Response:
    """Handle GET /api/v1/tasks"""
    return Response(status=200, body='[]')


def handle_tasks_create(request: Request) -> Response:
    """Handle POST /api/v1/tasks"""
    # Placeholder: Return created task
    body = {}
    try:
        import json
        if request.body:
            body = json.loads(request.body.decode())
    except Exception:
        pass

    task = {
        'id': 'task-placeholder-id',
        'baby_id': body.get('baby_id', ''),
        'title': body.get('title', ''),
        'points': body.get('points', 0),
        'type': body.get('type', 'checkin'),
        'tags': body.get('tags', []),
        'status': 'ongoing',
        'completed': 0,
        'total': 1,
        'created_at': '2026-05-18T00:00:00Z',
        'updated_at': '2026-05-18T00:00:00Z',
    }
    import json
    return Response(status=201, body=json.dumps(task))


def on_fetch(request: Request) -> Response:
    """
    Main request handler - routes to appropriate endpoint handlers.

    In production, this would be the exported handler for Cloudflare Workers:
        export default {
            async fetch(request, env, ctx):
                return on_fetch(request)
        }
    """
    path = request.path
    method = request.method

    # Auth endpoints
    if path == '/api/v1/auth/login' and method == 'POST':
        return handle_auth_login(request)

    # Babies endpoints
    if path == '/api/v1/babies' and method == 'GET':
        return handle_babies_list(request)

    # Tasks endpoints
    if path == '/api/v1/tasks' and method == 'GET':
        return handle_tasks_list(request)
    if path == '/api/v1/tasks' and method == 'POST':
        return handle_tasks_create(request)

    # Default: 404
    return Response(status=404, body='{"error": "Not found"}')


# For local testing
if __name__ == '__main__':
    # Test authentication
    req = Request('POST', '/api/v1/auth/login', body=b'{"api_key": "test", "api_secret": "test"}')
    resp = on_fetch(req)
    print(f'Auth response: {resp.status} - {resp.body}')

    # Test babies list
    req = Request('GET', '/api/v1/babies')
    resp = on_fetch(req)
    print(f'Babies response: {resp.status} - {resp.body}')

    # Test task creation
    req = Request('POST', '/api/v1/tasks', body=b'{"baby_id": "b1", "title": "Test Task", "points": 10}')
    resp = on_fetch(req)
    print(f'Task create response: {resp.status} - {resp.body}')