import uuid

from flask import jsonify, request, Blueprint

from .models import Prompt


bp = Blueprint('api', __name__)


@bp.route('/prompt/<prompt_id>', methods=['GET'])
def get_prompt_detail(prompt_id):
    try:
        prompt = Prompt.objects.get(prompt_id=prompt_id)
        prompt_data = {
            'prompt_id': prompt.prompt_id,
            'content': prompt.content,
            'variables': prompt.variables,
            'example': prompt.example,
            'version': prompt.version,
            'applicable_llm': prompt.applicable_llm,
            'created_at': prompt.created_at,
            'updated_at': prompt.updated_at,
            'tags': prompt.tags
        }
        return jsonify(prompt_data), 200
    except Prompt.DoesNotExist:
        return jsonify({'error': 'Prompt not found'}), 404
    except Exception:
        return jsonify({'error': 'Something went wrong. Please try again later.'}), 500


@bp.route('/prompt/<prompt_id>', methods=['PUT'])
def update_prompt(prompt_id):
    try:
        prompt = Prompt.objects.get(prompt_id=prompt_id)
        data = request.json
        if 'content' in data:
            prompt.content = data['content']
        if 'variables' in data:
            prompt.variables = data['variables']
        if 'example' in data:
            prompt.example = data['example']
        if 'version' in data:
            prompt.version = data['version']
        if 'applicable_llm' in data:
            prompt.applicable_llm = data['applicable_llm']
        if 'tags' in data:
            prompt.tags = data['tags']
        prompt.save()
        return jsonify({'message': 'Prompt updated successfully'}), 200
    except Prompt.DoesNotExist:
        return jsonify({'error': 'Prompt not found'}), 404
    except Exception:
        return jsonify({'error': 'Something went wrong. Please try again later.'}), 500


@bp.route('/prompt/<prompt_id>', methods=['DELETE'])
def delete_prompt(prompt_id):
    try:
        prompt = Prompt.objects.get(prompt_id=prompt_id)
        prompt.delete()
        return jsonify({'message': 'Prompt deleted successfully'}), 200
    except Prompt.DoesNotExist:
        return jsonify({'error': 'Prompt not found'}), 404
    except Exception:
        return jsonify({'error': 'Something went wrong. Please try again later.'}), 500


@bp.route('/prompt', methods=['POST'])
def create_prompt():
    try:
        data = request.json

        # Generate a unique prompt_id
        prompt_id = str(uuid.uuid4())

        prompt = Prompt(
            prompt_id=prompt_id,
            content=data['content'],
            variables=data['variables'],
            example=data['example'],
            version=data['version'],
            applicable_llm=data['applicable_llm'],
            tags=data['tags']
        )
        prompt.save()
        return jsonify({'message': 'Prompt created successfully', 'prompt_id': prompt_id}), 201
    except KeyError as e:
        return jsonify({'error': f'Missing required field: {e.args[0]}'}), 400
    except Exception:
        return jsonify({'error': 'Something went wrong. Please try again later.'}), 500


@bp.route('/prompts', methods=['GET'])
def get_prompt_list():
    try:
        # Get query parameters for filtering, searching, pagination, and sorting
        applicable_llm = request.args.get('applicable_llm')
        tag = request.args.get('tag')
        keywords = request.args.get('keywords')
        offset = int(request.args.get('offset', 0))  # Default to 0 if not provided
        limit = int(request.args.get('limit', 10))   # Default to 10 if not provided
        sort_by = request.args.get('sort_by', '-created_at')  # Default to sorting by created_at in descending order

        # Initialize the query to retrieve all prompts
        query = Prompt.objects

        # Apply filtering based on applicable_llm
        if applicable_llm:
            query = query.filter(applicable_llm=applicable_llm)

        # Apply filtering based on tags
        if tag:
            query = query.filter(tags__in=[tag])

        # Apply fuzzy search by keywords in content
        if keywords:
            query = query.search_text(keywords)

        # Apply sorting based on sort_by field
        query = query.order_by(sort_by)

        # Execute the query to retrieve prompts with pagination
        prompts = query.skip(offset).limit(limit)

        # Serialize prompts to JSON format
        prompt_list = []
        for prompt in prompts:
            prompt_data = {
                'prompt_id': prompt.prompt_id,
                'content': prompt.content,
                'variables': prompt.variables,
                'example': prompt.example,
                'version': prompt.version,
                'applicable_llm': prompt.applicable_llm,
                'created_at': prompt.created_at,
                'updated_at': prompt.updated_at,
                'tags': prompt.tags
            }
            prompt_list.append(prompt_data)

        return jsonify(prompt_list), 200

    except Exception:
        return jsonify({'error': 'Something went wrong. Please try again later.'}), 500
