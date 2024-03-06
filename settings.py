from decouple import config

ALLOWED_HOSTS = ['*']

port = int(config('PORT')) if config('PORT') is not None else 5000

DEBUG = True

if DEBUG:
    # Run the development server with the specified port
    RUNSERVER = f'0.0.0.0:{port}'
