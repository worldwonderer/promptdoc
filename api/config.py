import os


MONGODB_SETTINGS = {
    'db': 'prompt',
    'host': os.getenv("MONGODB_HOST")
}
