"""Run Django development server on port 3005."""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv(Path(__file__).resolve().parent / ".env")

if __name__ == "__main__":
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mountain_harvest.settings')
    
    from django.core.management import execute_from_command_line
    
    # Override runserver command to use port 3005
    if len(sys.argv) == 1:
        sys.argv = ['manage.py', 'runserver', '0.0.0.0:3005']
    elif sys.argv[1] == 'runserver' and len(sys.argv) == 2:
        sys.argv.append('0.0.0.0:3005')
    
    execute_from_command_line(sys.argv)
