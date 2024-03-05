import os

ALLOWED_HOSTS = ['*']

if 'PORT' in os.environ:
    port = int(os.environ.get('PORT'))
else:
    port = 8000

DEBUG = True

if DEBUG:
    # Run the development server with the specified port
    RUNSERVER = f'0.0.0.0:{port}'
