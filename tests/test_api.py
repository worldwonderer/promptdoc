import uuid

import pytest

pytestmark = pytest.mark.integration

from api import admin_routes
from api.models import Prompt, PromptVersion
from tests.helpers import TEST_MARKER_TAG, auth_headers, build_prompt_payload


@pytest.fixture(autouse=True)
def cleanup_test_prompts():
    yield
    Prompt.objects(tags__in=[TEST_MARKER_TAG]).delete()
    Prompt.objects(prompt_id__startswith='test-').delete()
    PromptVersion.objects(prompt_id__startswith='test-').delete()


@pytest.fixture
def created_prompt():
    data = build_prompt_payload(
        prompt_id=f"test-{uuid.uuid4()}",
    )
    prompt = Prompt(**data)
    prompt.save()
    yield prompt
    Prompt.objects(prompt_id=prompt.prompt_id).delete()


# --- Original tests ---


def test_create_prompt(client):
    response = client.post('/api/prompt', json=build_prompt_payload(), headers=auth_headers())
    assert response.status_code == 201
    assert 'prompt_id' in response.json


def test_get_prompt_list(client):
    response = client.get('/api/prompts', headers=auth_headers())
    assert response.status_code == 200
    assert isinstance(response.json['data'], list)


def test_get_prompt_list_rejects_invalid_page(client):
    response = client.get('/api/prompts?page=abc', headers=auth_headers())
    assert response.status_code == 400
    assert "Invalid 'page' parameter" in response.json['error']


def test_get_prompt_list_rejects_invalid_per_page(client):
    response = client.get('/api/prompts?per_page=0', headers=auth_headers())
    assert response.status_code == 400
    assert "Invalid 'per_page' parameter" in response.json['error']


def test_create_prompt_rejects_missing_required_fields(client):
    response = client.post('/api/prompt', json={'content': 'missing required'}, headers=auth_headers())
    assert response.status_code == 400
    assert response.json == {'error': 'Invalid request payload'}


def test_api_requires_configured_token(client, monkeypatch):
    monkeypatch.delenv('AUTH_TOKEN', raising=False)
    monkeypatch.delenv('AUTH_SECRET', raising=False)
    response = client.get('/api/prompts', headers=auth_headers(token='your_token_here'))
    assert response.status_code == 503
    assert response.json == {'error': 'Server authentication token is not configured'}


def test_update_prompt(client, created_prompt):
    updated_data = build_prompt_payload(
        content='Updated prompt content',
        variables=['variable1', 'variable2', 'variable3'],
        example={
            'variable1': 'updated_example1',
            'variable2': 'updated_example2',
            'variable3': 'example3',
        },
        version='2',
        applicable_llm='LLM2',
        tags=['tag1', 'tag3', TEST_MARKER_TAG],
    )

    response = client.put(
        f'/api/prompt/{created_prompt.prompt_id}',
        json=updated_data,
        headers=auth_headers(),
    )
    assert response.status_code == 200
    assert response.json == {'message': 'Prompt updated successfully'}

    updated_prompt = Prompt.objects.get(prompt_id=created_prompt.prompt_id)
    assert updated_prompt.content == updated_data['content']
    assert updated_prompt.variables == updated_data['variables']


def test_delete_prompt(client, created_prompt):
    response = client.delete(f'/api/prompt/{created_prompt.prompt_id}', headers=auth_headers())
    assert response.status_code == 200
    assert response.json == {'message': 'Prompt deleted successfully'}

    with pytest.raises(Prompt.DoesNotExist):
        Prompt.objects.get(prompt_id=created_prompt.prompt_id)


def test_admin_prompt_detail_not_found_returns_404(logged_in_client):
    response = logged_in_client.get('/admin/prompt/does-not-exist')
    assert response.status_code == 404


def test_admin_create_prompt_rejects_invalid_example(logged_in_client):
    response = logged_in_client.post(
        '/admin/prompt/create',
        data={
            'content': 'Hello {{name}}',
            'variables': 'name',
            'example': '{invalid',
            'version': '1',
            'applicable_llm': 'LLM1',
            'tags': TEST_MARKER_TAG,
        },
    )
    assert response.status_code == 400
    assert 'Invalid example format' in response.get_data(as_text=True)


def test_admin_edit_prompt_rejects_invalid_example(logged_in_client, created_prompt):
    response = logged_in_client.post(
        f'/admin/prompt/{created_prompt.prompt_id}/edit',
        data={
            'content': 'Updated {{name}}',
            'variables': 'name',
            'example': '{invalid',
            'version': '2',
            'applicable_llm': 'LLM2',
            'tags': TEST_MARKER_TAG,
        },
    )
    assert response.status_code == 400
    assert 'Invalid example format' in response.get_data(as_text=True)


def test_admin_preview_does_not_execute_template_expression(logged_in_client, created_prompt):
    created_prompt.update(
        content='Danger: {{7*7}} - {{variable1}}',
        example={'variable1': 'safe-value'},
    )
    created_prompt.reload()

    response = logged_in_client.get(f'/admin/prompt/{created_prompt.prompt_id}')
    page = response.get_data(as_text=True)

    assert response.status_code == 200
    assert 'Danger: {{7*7}} - safe-value' in page
    assert 'Danger: 49 - safe-value' not in page


def test_admin_login_returns_503_when_secret_missing(client, monkeypatch):
    monkeypatch.setattr(admin_routes, 'ADMIN_SECRET', None)
    response = client.post('/admin/login', data={'auth_code': '123456'})
    assert response.status_code == 503
    assert 'Admin secret is not configured' in response.get_data(as_text=True)


# --- New integration tests ---


def test_get_prompt_detail(client, created_prompt):
    response = client.get(f'/api/prompt/{created_prompt.prompt_id}', headers=auth_headers())
    assert response.status_code == 200
    assert response.json['prompt_id'] == created_prompt.prompt_id
    assert response.json['content'] == created_prompt.content


def test_get_prompt_detail_not_found(client):
    response = client.get('/api/prompt/nonexistent-id', headers=auth_headers())
    assert response.status_code == 404
    assert response.json == {'error': 'Prompt not found'}


def test_update_prompt_not_found(client):
    response = client.put('/api/prompt/nonexistent-id', json={'content': 'x'}, headers=auth_headers())
    assert response.status_code == 404


def test_delete_prompt_not_found(client):
    response = client.delete('/api/prompt/nonexistent-id', headers=auth_headers())
    assert response.status_code == 404


def test_update_prompt_partial(client, created_prompt):
    response = client.put(
        f'/api/prompt/{created_prompt.prompt_id}',
        json={'version': '2'},
        headers=auth_headers(),
    )
    assert response.status_code == 200
    updated = Prompt.objects.get(prompt_id=created_prompt.prompt_id)
    assert updated.version == '2'


def test_create_prompt_rejects_invalid_json(client):
    response = client.post(
        '/api/prompt',
        data='not json',
        headers={**auth_headers(), 'Content-Type': 'application/json'},
    )
    assert response.status_code == 400


def test_list_pagination_last_page(client):
    for i in range(3):
        data = build_prompt_payload(prompt_id=f"test-page-{uuid.uuid4()}", tags=[TEST_MARKER_TAG])
        Prompt(**data).save()

    response = client.get('/api/prompts?page=999&per_page=1', headers=auth_headers())
    assert response.status_code == 200
    assert response.json['pagination']['total_pages'] >= 1


def test_list_tag_filter(client):
    data = build_prompt_payload(
        prompt_id=f"test-tag-{uuid.uuid4()}",
        tags=['unique-filter-tag', TEST_MARKER_TAG],
    )
    Prompt(**data).save()

    response = client.get('/api/prompts?tag=unique-filter-tag', headers=auth_headers())
    assert response.status_code == 200
    assert len(response.json['data']) >= 1
    for p in response.json['data']:
        assert 'unique-filter-tag' in p['tags']


def test_list_search(client):
    data = build_prompt_payload(
        prompt_id=f"test-search-{uuid.uuid4()}",
        content='unique search content xyz123',
    )
    data['tags'] = [TEST_MARKER_TAG]
    Prompt(**data).save()

    response = client.get('/api/prompts?search=xyz123', headers=auth_headers())
    assert response.status_code == 200
    assert len(response.json['data']) >= 1


def test_api_rejects_invalid_token(client):
    response = client.get('/api/prompts', headers={'Authorization': 'Bearer wrong-token'})
    assert response.status_code == 401


def test_api_rejects_missing_auth_header(client):
    response = client.get('/api/prompts')
    assert response.status_code == 401


def test_update_creates_version_snapshot(client, created_prompt):
    updated_data = build_prompt_payload(content='Updated content', version='2')
    response = client.put(
        f'/api/prompt/{created_prompt.prompt_id}',
        json=updated_data,
        headers=auth_headers(),
    )
    assert response.status_code == 200

    versions = PromptVersion.objects(prompt_id=created_prompt.prompt_id)
    assert versions.count() == 1
    assert versions.first().content == 'Test prompt content'
    assert versions.first().version == '1'


def test_delete_creates_version_snapshot(client, created_prompt):
    response = client.delete(
        f'/api/prompt/{created_prompt.prompt_id}',
        headers=auth_headers(),
    )
    assert response.status_code == 200

    versions = PromptVersion.objects(prompt_id=created_prompt.prompt_id)
    assert versions.count() == 1
    assert versions.first().snapshot_reason == 'delete'


def test_get_prompt_versions(client, created_prompt):
    updated_data = build_prompt_payload(content='Updated', version='2')
    client.put(f'/api/prompt/{created_prompt.prompt_id}', json=updated_data, headers=auth_headers())

    response = client.get(f'/api/prompt/{created_prompt.prompt_id}/versions', headers=auth_headers())
    assert response.status_code == 200
    assert len(response.json['data']) == 1
    assert response.json['data'][0]['content'] == 'Test prompt content'


def test_get_version_diff(client, created_prompt):
    updated_data = build_prompt_payload(content='Completely new content', version='2')
    client.put(f'/api/prompt/{created_prompt.prompt_id}', json=updated_data, headers=auth_headers())

    version = PromptVersion.objects(prompt_id=created_prompt.prompt_id).first()
    response = client.get(
        f'/api/prompt/{created_prompt.prompt_id}/versions/{version.id}/diff',
        headers=auth_headers(),
    )
    assert response.status_code == 200
    assert 'diff' in response.json
    assert 'changes' in response.json
