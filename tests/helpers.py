import os
import uuid

TEST_MARKER_TAG = '__pytest__'


def build_prompt_payload(**overrides):
    payload = {
        'content': 'Test prompt content',
        'variables': ['variable1', 'variable2'],
        'example': {'variable1': 'example1', 'variable2': 'example2'},
        'version': '1',
        'applicable_llm': 'LLM1',
        'tags': ['tag1', TEST_MARKER_TAG],
    }
    payload.update(overrides)
    return payload


def auth_headers(token=None):
    auth_token = token if token is not None else os.getenv('AUTH_TOKEN', '')
    return {'Authorization': f'Bearer {auth_token}'}
