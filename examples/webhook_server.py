#!/usr/bin/env python3
"""
Webhook server example - demonstrates receiving and handling webhook events
from the Future Little Leaders platform.

Run this server to receive real-time notifications when events like
task.completed or achievement.unlocked occur.

Usage:
    python examples/webhook_server.py

The server will start on http://0.0.0.0:5000 by default.
Register this URL as your webhook endpoint in the FLL developer dashboard.
"""

import sys
import argparse
from fll_sdk.webhooks import WebhookServer
from fll_sdk.models import WebhookEvent


def handle_task_completed(event: WebhookEvent) -> None:
    """Handle task.completed webhook event."""
    data = event.data
    print(f'[TASK COMPLETED] Task {data.get("task_id")} completed by baby {data.get("baby_id")}')
    print(f'  Points earned: {data.get("points", 0)}')
    print(f'  Timestamp: {data.get("completed_at", "unknown")}')


def handle_achievement_unlocked(event: WebhookEvent) -> None:
    """Handle achievement.unlocked webhook event."""
    data = event.data
    print(f'[ACHIEVEMENT UNLOCKED] Baby {data.get("baby_id")} unlocked "{data.get("achievement_name")}"')
    print(f'  Achievement ID: {data.get("achievement_id")}')
    print(f'  Icon: {data.get("icon", "N/A")}')


def handle_points_changed(event: WebhookEvent) -> None:
    """Handle points.changed webhook event."""
    data = event.data
    print(f'[POINTS CHANGED] Baby {data.get("baby_id")}')
    print(f'  Old balance: {data.get("old_balance", 0)}')
    print(f'  New balance: {data.get("new_balance", 0)}')
    print(f'  Reason: {data.get("reason", "N/A")}')


def handle_skill_node_unlocked(event: WebhookEvent) -> None:
    """Handle skill_node.unlocked webhook event."""
    data = event.data
    print(f'[SKILL NODE UNLOCKED] Baby {data.get("baby_id")} unlocked skill node')
    print(f'  Node ID: {data.get("node_id")}')
    print(f'  Node name: {data.get("node_name", "unknown")}')


def handle_streak_warning(event: WebhookEvent) -> None:
    """Handle streak.warning webhook event."""
    data = event.data
    print(f'[STREAK WARNING] Baby {data.get("baby_id")} - streak at risk!')
    print(f'  Current streak: {data.get("streak_count", 0)} days')
    print(f'  Last check-in: {data.get("last_checkin", "unknown")}')


def handle_flow_started(event: WebhookEvent) -> None:
    """Handle flow.started webhook event."""
    data = event.data
    print(f'[FLOW STARTED] Flow "{data.get("flow_name")}" started for baby {data.get("baby_id")}')
    print(f'  Flow ID: {data.get("flow_id")}')


def main():
    parser = argparse.ArgumentParser(description='FLL Webhook Server Example')
    parser.add_argument(
        '--secret',
        default='your-webhook-secret',
        help='Webhook secret for signature verification'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=5000,
        help='Port to listen on (default: 5000)'
    )
    args = parser.parse_args()

    # Initialize webhook server
    server = WebhookServer(secret=args.secret)

    # Register event handlers
    server.register('task.completed', handle_task_completed)
    server.register('achievement.unlocked', handle_achievement_unlocked)
    server.register('points.changed', handle_points_changed)
    server.register('skill_node.unlocked', handle_skill_node_unlocked)
    server.register('streak.warning', handle_streak_warning)
    server.register('flow.started', handle_flow_started)

    print(f'=' * 60)
    print('Future Little Leaders - Webhook Server')
    print(f'=' * 60)
    print(f'Listening for webhook events on port {args.port}')
    print(f'Secret: {args.secret}')
    print()
    print('Registered events:')
    print('  - task.completed')
    print('  - achievement.unlocked')
    print('  - points.changed')
    print('  - skill_node.unlocked')
    print('  - streak.warning')
    print('  - flow.started')
    print()
    print('Press Ctrl+C to stop')
    print(f'=' * 60)

    try:
        server.run(port=args.port)
    except KeyboardInterrupt:
        print('\nShutting down...')
        server.stop()
        sys.exit(0)


if __name__ == '__main__':
    main()