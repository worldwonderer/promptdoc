import os
import ast
import uuid
import json
import re
import difflib
from functools import wraps
from datetime import datetime

import pyotp
from flask_babel import gettext as _
from marshmallow.exceptions import ValidationError
from flask import render_template, Blueprint, request, redirect, session, url_for, abort

from .models import Prompt, PromptSchema, PromptVersion, create_version_snapshot


admin_bp = Blueprint('admin', __name__, url_prefix='/admin')
ADMIN_SECRET = os.environ.get('ADMIN_SECRET')
TEMPLATE_VAR_PATTERN = re.compile(r'\{\{\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\}\}')


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated_function


@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if not ADMIN_SECRET:
        return _('Admin secret is not configured'), 503
    if request.method == 'POST':
        auth_code = request.form.get('auth_code', '').strip()
        totp = pyotp.TOTP(ADMIN_SECRET)
        if totp.verify(auth_code):
            session['logged_in'] = True
            session.permanent = True  # 设置session为永久性的
            return redirect(url_for('admin.prompt_list'))
        else:
            return _('Invalid auth code'), 403
    else:
        return render_template('login.html')


def handle_form_data(form):
    form_data = form.to_dict()
    # Assuming tags are submitted as a comma-separated string
    tags_str = form_data.get('tags', '')
    form_data['tags'] = [tag.strip() for tag in tags_str.split(',')] if tags_str else []
    variables_str = form_data.get('variables', '')
    form_data['variables'] = [variable.strip() for variable in
                              variables_str.split(',')] if variables_str else []
    example_str = form_data.get('example', '').strip()
    if not example_str:
        form_data['example'] = {}
    else:
        try:
            parsed_example = ast.literal_eval(example_str)
        except (ValueError, SyntaxError):
            raise ValidationError({'example': [_('Invalid example format. Please provide a valid dictionary.')]})
        if not isinstance(parsed_example, dict):
            raise ValidationError({'example': [_('Invalid example format. Please provide a valid dictionary.')]})
        form_data['example'] = parsed_example
    return form_data


def get_prompt_or_404(prompt_id):
    try:
        return Prompt.objects.get(prompt_id=prompt_id)
    except Prompt.DoesNotExist:
        abort(404, description=_('Prompt not found'))


def render_prompt_preview(content, example):
    if not isinstance(content, str):
        return ''
    if not isinstance(example, dict):
        return content

    def replace_var(match):
        key = match.group(1)
        if key not in example:
            return match.group(0)
        value = example[key]
        if isinstance(value, (dict, list)):
            return json.dumps(value, ensure_ascii=False)
        return str(value)

    return TEMPLATE_VAR_PATTERN.sub(replace_var, content)


@admin_bp.route('/prompts')
@login_required
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
@login_required
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
            return render_template('prompt_form.html', errors=e.messages), 400
        except Exception as e:
            # 处理其他错误,可以在页面上显示一般性错误消息
            return render_template('prompt_form.html', error=_('Failed to create prompt')), 500
    return render_template('prompt_form.html')


@admin_bp.route('/prompt/<prompt_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_prompt(prompt_id):
    prompt = get_prompt_or_404(prompt_id)
    if request.method == 'POST':
        try:
            form_data = handle_form_data(request.form)
            # Validate and deserialize the form data with PromptSchema
            prompt_schema = PromptSchema(partial=True)
            prompt_schema.load(form_data)
            create_version_snapshot(prompt)
            prompt.update(**form_data)
            prompt.updated_at = datetime.now()
            prompt.save()
            return redirect('/admin/prompts')
        except ValidationError as e:
            return render_template('prompt_form.html', prompt=prompt, errors=e.messages), 400
        except Exception:
            return render_template('prompt_form.html', prompt=prompt, error=_('Failed to update prompt')), 500
    return render_template('prompt_form.html', prompt=prompt)


@admin_bp.route('/prompt/<prompt_id>/delete', methods=['POST'])
@login_required
def delete_prompt(prompt_id):
    prompt = get_prompt_or_404(prompt_id)
    create_version_snapshot(prompt, reason='delete')
    prompt.delete()
    return redirect('/admin/prompts')


@admin_bp.route('/prompt/<prompt_id>')
@login_required
def prompt_detail(prompt_id):
    prompt = get_prompt_or_404(prompt_id)
    formatted_prompt = render_prompt_preview(prompt.content, prompt.example)
    version_count = PromptVersion.objects(prompt_id=prompt_id).count()
    return render_template('prompt_detail.html', prompt=prompt, formatted_prompt=formatted_prompt, version_count=version_count)


def _compute_field_changes(newer, version):
    changes = {}
    if newer:
        if newer.version != version.version:
            changes['version'] = {'from': newer.version, 'to': version.version}
        if newer.applicable_llm != version.applicable_llm:
            changes['applicable_llm'] = {'from': newer.applicable_llm, 'to': version.applicable_llm}
        if set(newer.tags or []) != set(version.tags or []):
            changes['tags'] = {'from': newer.tags, 'to': version.tags}
        if set(newer.variables or []) != set(version.variables or []):
            changes['variables'] = {'from': newer.variables, 'to': version.variables}
        if newer.example != version.example:
            changes['example'] = {'from': newer.example, 'to': version.example}
    return changes


@admin_bp.route('/prompt/<prompt_id>/history')
@login_required
def prompt_history(prompt_id):
    prompt = get_prompt_or_404(prompt_id)
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))

    query = PromptVersion.objects(prompt_id=prompt_id).order_by('-snapshot_at')
    total_count = query.count()
    versions = query.skip((page - 1) * per_page).limit(per_page)

    return render_template(
        'prompt_history.html',
        prompt=prompt,
        versions=versions,
        total_count=total_count,
        page=page,
        per_page=per_page,
    )


@admin_bp.route('/prompt/<prompt_id>/version/<version_id>')
@login_required
def prompt_version_detail(prompt_id, version_id):
    prompt = get_prompt_or_404(prompt_id)
    version = PromptVersion.objects.get(id=version_id, prompt_id=prompt_id)

    newer = PromptVersion.objects(
        prompt_id=prompt_id,
        snapshot_at__gt=version.snapshot_at,
    ).order_by('snapshot_at').first()

    old_content = newer.content if newer else ''
    diff_lines = list(difflib.unified_diff(
        old_content.splitlines(keepends=True),
        version.content.splitlines(keepends=True),
        lineterm='',
    ))

    changes = _compute_field_changes(newer, version)

    return render_template(
        'prompt_version_detail.html',
        prompt=prompt,
        version=version,
        diff_lines=diff_lines,
        changes=changes,
        has_previous=newer is not None,
    )
