import ast
import uuid
from marshmallow.exceptions import ValidationError
from flask import render_template, Blueprint, request, redirect

from .models import Prompt, PromptSchema


admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


def handle_form_data(form):
    form_data = form.to_dict()
    # Assuming tags are submitted as a comma-separated string
    tags_str = form_data.get('tags', '')
    form_data['tags'] = [tag.strip() for tag in tags_str.split(',')] if tags_str else []
    variables_str = form_data.get('variables', '')
    form_data['variables'] = [variable.strip() for variable in
                              variables_str.split(',')] if variables_str else []
    form_data['example'] = ast.literal_eval(form_data['example'])
    return form_data


@admin_bp.route('/prompts')
def prompt_list():
    tag = request.args.get('tag')
    search = request.args.get('search')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    sort_by = '-created_at'

    query = Prompt.objects.order_by(sort_by)

    if tag:
        query = query.filter(tags=tag)

    if search:
        query = query.filter(content__icontains=search)

    total_count = query.count()
    prompts = query.skip((page - 1) * per_page).limit(per_page)

    return render_template(
        'prompts.html',
        prompts=prompts,
        total_count=total_count,
        page=page,
        per_page=per_page
    )


@admin_bp.route('/prompt/create', methods=['GET', 'POST'])
def create_prompt():
    if request.method == 'POST':
        try:
            form_data = handle_form_data(request.form)
            prompt_schema = PromptSchema(partial=True)
            prompt = prompt_schema.load(form_data)
            prompt_id = str(uuid.uuid4())
            prompt.prompt_id = prompt_id
            prompt.save()
            return redirect('/admin/prompts')
        except ValidationError as e:
            # 处理验证错误,可以在页面上显示错误消息
            return render_template('prompt_form.html', errors=e.messages)
        except Exception as e:
            # 处理其他错误,可以在页面上显示一般性错误消息
            return render_template('prompt_form.html', error='Failed to create prompt')
    return render_template('prompt_form.html')


@admin_bp.route('/prompt/<prompt_id>/edit', methods=['GET', 'POST'])
def edit_prompt(prompt_id):
    prompt = Prompt.objects.get(prompt_id=prompt_id)
    if request.method == 'POST':
        form_data = handle_form_data(request.form)
        # Validate and deserialize the form data with PromptSchema
        prompt_schema = PromptSchema(partial=True)
        prompt_schema.load(form_data)
        prompt.update(**form_data)
        prompt.save()
        return redirect('/admin/prompts')
    return render_template('prompt_form.html', prompt=prompt)


@admin_bp.route('/prompt/<prompt_id>/delete', methods=['POST'])
def delete_prompt(prompt_id):
    prompt = Prompt.objects.get(prompt_id=prompt_id)
    prompt.delete()
    return redirect('/admin/prompts')


@admin_bp.route('/prompt/<prompt_id>')
def prompt_detail(prompt_id):
    prompt = Prompt.objects.get(prompt_id=prompt_id)
    return render_template('prompt_detail.html', prompt=prompt)