#!/usr/bin/env python3
"""
School sync example - demonstrates batch synchronization of student data
from a school management system to the Future Little Leaders platform.

This is a sample implementation showing how to use the fll_sdk package
to integrate with school/training institution management systems.
"""

import sys
from fll_sdk import FLLClient


def sync_students_from_school_db(client: FLLClient):
    """
    Simulate syncing student data from a school database.

    In a real implementation, this would connect to the school's
    student information system and fetch student records.
    """
    # Simulated school database records
    school_students = [
        {'name': '张小明', 'birthdate': '2019-03-15', 'gender': 'male'},
        {'name': '李小红', 'birthdate': '2019-05-22', 'gender': 'female'},
        {'name': '王小华', 'birthdate': '2018-11-08', 'gender': 'male'},
    ]

    print(f'Starting sync for {len(school_students)} students...')

    for student in school_students:
        try:
            baby = client.babies.create(
                name=student['name'],
                birthdate=student['birthdate'],
                gender=student['gender'],
            )
            print(f'  Created baby record: {baby.name} (ID: {baby.id})')

            # Create default daily check-in task
            task = client.tasks.create(
                baby_id=baby.id,
                title=f'{baby.name} - Daily Check-in',
                points=5,
                type='checkin',
                tags=['daily', 'school'],
                description='Daily morning health check-in',
            )
            print(f'    Created task: {task.title} (ID: {task.id})')

        except Exception as e:
            print(f'  Error syncing student {student["name"]}: {e}')

    print('Sync complete!')


def main():
    # Initialize client (uses environment variables or provided credentials)
    api_key = 'your-api-key'
    api_secret = 'your-api-secret'

    client = FLLClient(
        api_key=api_key,
        api_secret=api_secret,
        base_url='https://api.futurelittleleaders.example',
    )

    try:
        # Authenticate
        print('Authenticating...')
        token = client.login()
        print(f'Authenticated successfully (token: {token[:20]}...)')

        # Sync students
        sync_students_from_school_db(client)

    except Exception as e:
        print(f'Error: {e}')
        sys.exit(1)


if __name__ == '__main__':
    main()