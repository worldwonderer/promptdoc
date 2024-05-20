import uuid
import logging

from flask import jsonify, request, Blueprint
from marshmallow import ValidationError

from .models import Prompt, PromptSchema

bp = Blueprint('api', __name__, url_prefix='/api')

logger = logging.getLogger(__name__)


def error_response(message, status_code):
    return jsonify({'error': message}), status_code


@bp.route('/prompt/<prompt_id>', methods=['GET'])
def get_prompt_detail(prompt_id):
    """
    Get detailed information of a specific prompt.

    :param prompt_id: The unique identifier of the prompt.
    :return: JSON response containing the prompt details.
    """
    try:
        prompt = Prompt.objects.get(prompt_id=prompt_id)
        prompt_schema = PromptSchema()
        prompt_data = prompt_schema.dump(prompt)
        return jsonify(prompt_data), 200
    except Prompt.DoesNotExist:
        logger.exception(f"Prompt not found: {prompt_id}")
        return error_response('Prompt not found', 404)
    except Exception as e:
        logger.exception(f"Error retrieving prompt: {str(e)}")
        return error_response('Failed to retrieve prompt', 500)


@bp.route('/prompt/<prompt_id>', methods=['PUT'])
def update_prompt(prompt_id):
    """
    Update an existing prompt.

    :param prompt_id: The unique identifier of the prompt to update.
    :return: JSON response indicating the success or failure of the update operation.
    """
    try:
        prompt = Prompt.objects.get(prompt_id=prompt_id)
        prompt_schema = PromptSchema(partial=True)
        prompt_schema.load(request.json)
        prompt.update(**request.json)
        prompt.save()
        logger.info(f"Prompt updated successfully: {prompt_id}")
        return jsonify({'message': 'Prompt updated successfully'}), 200
    except Prompt.DoesNotExist:
        logger.exception(f"Prompt not found: {prompt_id}")
        return error_response('Prompt not found', 404)
    except ValidationError as e:
        logger.exception(f"Invalid request payload: {str(e)}")
        return error_response('Invalid request payload', 400)
    except Exception as e:
        logger.exception(f"Error updating prompt: {str(e)}")
        return error_response('Failed to update prompt', 500)


@bp.route('/prompt/<prompt_id>', methods=['DELETE'])
def delete_prompt(prompt_id):
    """
    Delete a prompt.

    :param prompt_id: The unique identifier of the prompt to delete.
    :return: JSON response indicating the success or failure of the delete operation.
    """
    try:
        prompt = Prompt.objects.get(prompt_id=prompt_id)
        prompt.delete()
        logger.info(f"Prompt deleted successfully: {prompt_id}")
        return jsonify({'message': 'Prompt deleted successfully'}), 200
    except Prompt.DoesNotExist:
        logger.exception(f"Prompt not found: {prompt_id}")
        return error_response('Prompt not found', 404)
    except Exception as e:
        logger.exception(f"Error deleting prompt: {str(e)}")
        return error_response('Failed to delete prompt', 500)


@bp.route('/prompt', methods=['POST'])
def create_prompt():
    """
    Create a new prompt.

    :return: JSON response containing the success message and the ID of the newly created prompt.
    """
    try:
        prompt_schema = PromptSchema(partial=True)
        prompt = prompt_schema.load(request.json)
        prompt_id = str(uuid.uuid4())
        prompt.prompt_id = prompt_id
        prompt.save()
        logger.info(f"Prompt created successfully: {prompt_id}")
        return jsonify({'message': 'Prompt created successfully', 'prompt_id': prompt_id}), 201
    except ValidationError as e:
        logger.exception(f"Invalid request payload: {str(e)}")
        return error_response('Invalid request payload', 400)
    except Exception as e:
        logger.exception(f"Error creating prompt: {str(e)}")
        return error_response('Failed to create prompt', 500)


@bp.route('/prompts', methods=['GET'])
def get_prompt_list():
    """
    Get a list of prompts with pagination, filtering, and sorting.

    Query Parameters:
    - applicable_llm: Filter prompts by applicable LLM.
    - tag: Filter prompts by tag.
    - keywords: Search prompts by keywords in content.
    - cursor: The cursor for pagination (default: None).
    - limit: The maximum number of prompts to return per page (default: 10, max: 100).
    - sort_by: The field to sort the prompts by (default: '-created_at').

    :return: JSON response containing the list of prompts.
    """
    try:
        applicable_llm = request.args.get('applicable_llm')
        tag = request.args.get('tag')
        keywords = request.args.get('keywords')
        cursor = request.args.get('cursor')
        limit = max(1, min(100, int(request.args.get('limit', 10))))  # Clamp limit between 1 and 100
        sort_by = request.args.get('sort_by', '-created_at')

        query = Prompt.objects
        if applicable_llm:
            query = query.filter(applicable_llm=applicable_llm)
        if tag:
            query = query.filter(tags__in=[tag])
        if keywords:
            query = query.search_text(keywords)
        query = query.order_by(sort_by)
        if cursor:
            query = query.filter(id__gt=cursor)

        prompts = query.limit(limit + 1)
        has_more = prompts.count() > limit
        prompts = prompts[:limit]
        next_cursor = str(prompts[-1].id) if has_more else None

        prompt_schema = PromptSchema(many=True)
        prompt_list = prompt_schema.dump(prompts)

        response_data = {
            'prompts': prompt_list,
            'has_more': has_more,
            'next_cursor': next_cursor
        }
        return jsonify(response_data), 200
    except Exception as e:
        logger.exception(f"Error retrieving prompts: {str(e)}")
        return error_response('Failed to retrieve prompts', 500)
