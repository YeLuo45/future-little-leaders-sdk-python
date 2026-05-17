# Future Little Leaders Python SDK

Python SDK for integrating with the Future Little Leaders educational platform.

## Installation

```bash
pip install fll-sdk
```

Or for development:

```bash
pip install -e .
```

## Quick Start

```python
from fll_sdk import FLLClient

# Initialize and authenticate
client = FLLClient(
    api_key='your-api-key',
    api_secret='your-api-secret'
)
client.login()

# List babies
babies = client.babies.list()

# Create a task
task = client.tasks.create(
    baby_id='baby-123',
    title='Morning Check-in',
    points=10,
    type='checkin'
)

# Complete the task
client.tasks.complete(task.id)
```

## Features

- **Babies/Children Management**: Create and manage child profiles
- **Task Management**: Create, update, and complete tasks with points
- **Achievements**: View and unlock achievements
- **Notifications**: List and manage notifications
- **Points System**: Check balances and award points
- **Webhooks**: Subscribe to real-time events

## Webhook Server

```python
from fll_sdk.webhooks import WebhookServer

server = WebhookServer(secret='your-webhook-secret')

def on_task_completed(event):
    print(f"Task {event.data['task_id']} completed!")

server.register('task.completed', on_task_completed)
server.run(port=5000)
```

## API Reference

See the full API documentation for detailed endpoint descriptions.

## License

MIT