import uuid
from marshmallow.exceptions import ValidationError
from flask import render_template, Blueprint, request, redirect

from .models import Prompt, PromptSchema


admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.route('/prompts')
def prompt_list():
    tag = request.args.get('tag')
    sort_by = '-created_at'
    if tag:
        prompts = Prompt.objects(tags=tag).order_by(sort_by)
    else:
        prompts = Prompt.objects.all().order_by(sort_by)
    return render_template('prompts.html', prompts=prompts)


@admin_bp.route('/prompt/create', methods=['GET', 'POST'])
def create_prompt():
    if request.method == 'POST':
        try:
            prompt_schema = PromptSchema()
            data = prompt_schema.load(request.form)
            prompt_id = str(uuid.uuid4())
            prompt = Prompt(prompt_id=prompt_id, version=1, **data)
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
        prompt_schema = PromptSchema(partial=True)
        data = prompt_schema.load(request.form)
        prompt.update(**data)
        prompt.version += 1
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