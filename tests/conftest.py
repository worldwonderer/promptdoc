import os

import pytest

os.environ.setdefault('AUTH_TOKEN', 'test_auth_token')
os.environ.setdefault('ADMIN_SECRET', 'JBSWY3DPEHPK3PXP')

from api.index import app


@pytest.fixture
def client():
    with app.test_client() as client:
        yield client


@pytest.fixture
def logged_in_client(client):
    with client.session_transaction() as session_data:
        session_data['logged_in'] = True
    return client
