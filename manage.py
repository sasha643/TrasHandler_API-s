#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trashapi.settings')

    # Insert superuser creation code
    try:
        from django.core.management import execute_from_command_line
        # Only create superuser if running the server or specified command
        if 'runserver' in sys.argv or 'createsuperuser' in sys.argv:
            from django.contrib.auth.models import User

            # Parameters for the superuser
            username = 'TrasHandler'
            email = 'TrasHandler@gmail.com'
            password = 'Scrap@123'

            # Create superuser if it doesn't exist
            if not User.objects.filter(username=username).exists():
                User.objects.create_superuser(username, email, password)
                print(f"Superuser '{username}' created successfully.")
            else:
                print(f"Superuser '{username}' already exists.")
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
