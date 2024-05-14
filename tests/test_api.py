import pytest

from api.index import app
from api.models import Prompt


@pytest.fixture
def client():
    with app.test_client() as client:
        yield client


def test_create_prompt(client):
    # Define the data for creating a new prompt
    data = {
        'content': 'Test prompt content',
        'variables': ['variable1', 'variable2'],
        'example': {'variable1': 'example1', 'variable2': 'example2'},
        'version': '1.0',
        'applicable_llm': 'LLM1',
        'tags': ['tag1', 'tag2']
    }

    # Make a POST request to create a new prompt
    response = client.post('/prompt', json=data)

    # Check that the response status code is 201 (Created)
    assert response.status_code == 201

    # Check that the response body contains the expected message
    # assert response.json == {'message': 'Prompt created successfully'}

    # Optionally, you can check other aspects of the response, such as the prompt ID returned
    # assert 'prompt_id' in response.json


def test_get_prompt_list(client):
    # Make a GET request to retrieve the list of prompts
    response = client.get('/prompts')

    # Check that the response status code is 200 (OK)
    assert response.status_code == 200

    # Check that the response body is a JSON array
    assert isinstance(response.json, list)

    # Optionally, you can check other aspects of the response, such as the number of prompts returned
    # assert len(response.json) == expected_number_of_prompts


@pytest.fixture
def created_prompt():
    # Create a prompt document for testing
    data = {
        'prompt_id': 'test_id',
        'content': 'Test prompt content',
        'variables': ['variable1', 'variable2'],
        'example': {'variable1': 'example1', 'variable2': 'example2'},
        'version': '1.0',
        'applicable_llm': 'LLM1',
        'tags': ['tag1', 'tag2']
    }
    prompt = Prompt(**data)
    prompt.save()
    yield prompt
    # Delete the prompt document after the test
    prompt.delete()


def test_update_prompt(client, created_prompt):
    # Define the updated data for the prompt
    updated_data = {
        'content': 'Updated prompt content',
        'variables': ['variable1', 'variable2', 'variable3'],
        'example': {'variable1': 'updated_example1', 'variable2': 'updated_example2', 'variable3': 'example3'},
        'version': '2.0',
        'applicable_llm': 'LLM2',
        'tags': ['tag1', 'tag3']
    }

    # Make a PUT request to update the prompt with the updated data
    response = client.put(f'/prompt/{created_prompt.prompt_id}', json=updated_data)

    # Check that the response status code is 200 (OK)
    assert response.status_code == 200

    # Check that the response body contains the expected message
    assert response.json == {'message': 'Prompt updated successfully'}

    # Optionally, you can check that the prompt has been updated in the database
    updated_prompt = Prompt.objects.get(prompt_id=created_prompt.prompt_id)
    assert updated_prompt.content == updated_data['content']
    assert updated_prompt.variables == updated_data['variables']
    # Add assertions for other fields as needed


def test_delete_prompt(client, created_prompt):
    # Make a DELETE request to delete the prompt
    response = client.delete(f'/prompt/{created_prompt.prompt_id}')

    # Check that the response status code is 200 (OK)
    assert response.status_code == 200

    # Check that the response body contains the expected message
    assert response.json == {'message': 'Prompt deleted successfully'}

    # Optionally, you can check that the prompt has been deleted from the database
    with pytest.raises(Prompt.DoesNotExist):
        Prompt.objects.get(prompt_id=created_prompt.prompt_id)