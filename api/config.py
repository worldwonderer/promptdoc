import os


MONGODB_SETTINGS = {
    'db': 'prompt',
    'host': os.getenv("MONGODB_HOST")
}

DEFAULT_AUTH_TOKEN_PLACEHOLDER = 'your_token_here'


def get_auth_token():
    token = os.getenv('AUTH_TOKEN', '').strip()
    if not token or token == DEFAULT_AUTH_TOKEN_PLACEHOLDER:
        return None
    return token
