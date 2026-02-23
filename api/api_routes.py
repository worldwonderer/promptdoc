import uuid
import logging
from functools import wraps
from datetime import datetime

from flask import jsonify, request, Blueprint
from marshmallow import ValidationError
from mongoengine.errors import ValidationError as MongoValidationError

from .models import Prompt, PromptSchema
from .config import get_auth_token

bp = Blueprint('api', __name__, url_prefix='/api')

logger = logging.getLogger(__name__)

MAX_PER_PAGE = 100


def error_response(message, status_code):
    return jsonify({'error': message}), status_code


def parse_positive_int_arg(name, default_value, max_value=None):
    raw_value = request.args.get(name, str(default_value))
    try:
        value = int(raw_value)
    except (TypeError, ValueError):
        return None, f"Invalid '{name}' parameter: must be an integer."
    if value < 1:
        return None, f"Invalid '{name}' parameter: must be greater than 0."
    if max_value is not None and value > max_value:
        return None, f"Invalid '{name}' parameter: must be less than or equal to {max_value}."
    return value, None


def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        configured_token = get_auth_token()
        if not configured_token:
            logger.error('API auth token is not configured. Set AUTH_TOKEN.')
            return error_response('Server authentication token is not configured', 503)
        token = request.headers.get('Authorization')
        if token != f"Bearer {configured_token}":
            return error_response('Unauthorized', 401)
        return f(*args, **kwargs)
    return decorated_function


@bp.route('/prompt/<prompt_id>', methods=['GET'])
@token_required
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
@token_required
def update_prompt(prompt_id):
    """
    Update an existing prompt.

    :param prompt_id: The unique identifier of the prompt to update.
    :return: JSON response indicating the success or failure of the update operation.
    """
    try:
        prompt = Prompt.objects.get(prompt_id=prompt_id)
        payload = request.get_json(silent=True)
        if payload is None or not isinstance(payload, dict):
            return error_response('Invalid request payload', 400)
        prompt_schema = PromptSchema(partial=True)
        validation_errors = prompt_schema.validate(payload, partial=True)
        if validation_errors:
            raise ValidationError(validation_errors)
        payload.pop('prompt_id', None)
        payload['updated_at'] = datetime.now()
        prompt.update(**payload)
        logger.info(f"Prompt updated successfully: {prompt_id}")
        return jsonify({'message': 'Prompt updated successfully'}), 200
    except Prompt.DoesNotExist:
        logger.exception(f"Prompt not found: {prompt_id}")
        return error_response('Prompt not found', 404)
    except (ValidationError, MongoValidationError) as e:
        logger.exception(f"Invalid request payload: {str(e)}")
        return error_response('Invalid request payload', 400)
    except Exception as e:
        logger.exception(f"Error updating prompt: {str(e)}")
        return error_response('Failed to update prompt', 500)


@bp.route('/prompt/<prompt_id>', methods=['DELETE'])
@token_required
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
@token_required
def create_prompt():
    """
    Create a new prompt.

    :return: JSON response containing the success message and the ID of the newly created prompt.
    """
    try:
        payload = request.get_json(silent=True)
        if payload is None or not isinstance(payload, dict):
            return error_response('Invalid request payload', 400)
        prompt_id = str(uuid.uuid4())
        payload = {**payload, 'prompt_id': prompt_id}
        prompt_schema = PromptSchema(partial=True)
        validation_errors = prompt_schema.validate(payload)
        if validation_errors:
            raise ValidationError(validation_errors)
        prompt = prompt_schema.load(payload)
        prompt.save()
        logger.info(f"Prompt created successfully: {prompt_id}")
        return jsonify({'message': 'Prompt created successfully', 'prompt_id': prompt_id}), 201
    except (ValidationError, MongoValidationError) as e:
        logger.exception(f"Invalid request payload: {str(e)}")
        return error_response('Invalid request payload', 400)
    except Exception as e:
        logger.exception(f"Error creating prompt: {str(e)}")
        return error_response('Failed to create prompt', 500)


@bp.route('/prompts', methods=['GET'])
@token_required
def get_prompt_list():
    """
    Get a list of prompts with optional filtering and pagination.

    :return: JSON response containing the list of prompts and pagination information.
    """
    try:
        tag = request.args.get('tag')
        search = request.args.get('search')
        page, error = parse_positive_int_arg('page', 1)
        if error:
            return error_response(error, 400)
        per_page, error = parse_positive_int_arg('per_page', 10, max_value=MAX_PER_PAGE)
        if error:
            return error_response(error, 400)
        sort_by = '-created_at'

        query = Prompt.objects.order_by(sort_by)

        if tag:
            query = query.filter(tags__in=[tag])

        if search:
            query = query.filter(content__icontains=search)

        total_count = query.count()
        prompts = query.skip((page - 1) * per_page).limit(per_page)

        prompt_schema = PromptSchema(many=True)
        prompt_data = prompt_schema.dump(prompts)

        return jsonify({
            'data': prompt_data,
            'pagination': {
                'total_count': total_count,
                'page': page,
                'per_page': per_page,
                'total_pages': (total_count + per_page - 1) // per_page
            }
        }), 200
    except Exception as e:
        logger.error(f"Error retrieving prompt list: {str(e)}")
        return jsonify({'error': 'Failed to retrieve prompt list'}), 500
