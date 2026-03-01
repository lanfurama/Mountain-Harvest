#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mountain_harvest.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    
    # Override default port to 3005 for runserver command
    if len(sys.argv) >= 2 and sys.argv[1] == 'runserver':
        # If no port specified, use 3005
        if len(sys.argv) == 2:
            sys.argv.append('0.0.0.0:3005')
        # If only IP specified without port, add port 3005
        elif len(sys.argv) == 3 and ':' not in sys.argv[2]:
            sys.argv[2] = f"{sys.argv[2]}:3005"
    
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
