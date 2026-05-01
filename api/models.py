from datetime import datetime

from marshmallow_mongoengine import ModelSchema
from mongoengine import Document, StringField, ListField, DateTimeField, DictField, BooleanField


class Prompt(Document):
    prompt_id = StringField(required=True, unique=True)
    content = StringField(required=True)
    variables = ListField(StringField())
    example = DictField()
    version = StringField(required=True)
    applicable_llm = StringField(required=True)
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)
    tags = ListField(StringField())
    share_token = StringField(unique=True, sparse=True)
    is_public = BooleanField(default=False)

    meta = {'collection': 'prompts'}


class PromptVersion(Document):
    prompt_id = StringField(required=True)
    content = StringField(required=True)
    variables = ListField(StringField())
    example = DictField()
    version = StringField(required=True)
    applicable_llm = StringField(required=True)
    tags = ListField(StringField())
    snapshot_at = DateTimeField(default=datetime.now)
    snapshot_reason = StringField(default='update')

    meta = {
        'collection': 'prompt_versions',
        'indexes': [{'fields': ['prompt_id', '-snapshot_at']}],
        'ordering': ['-snapshot_at'],
    }


class PromptSchema(ModelSchema):
    class Meta:
        model = Prompt
        exclude = ['id']


def create_version_snapshot(prompt, reason='update'):
    return PromptVersion(
        prompt_id=prompt.prompt_id,
        content=prompt.content,
        variables=list(prompt.variables) if prompt.variables else [],
        example=dict(prompt.example) if prompt.example else {},
        version=prompt.version,
        applicable_llm=prompt.applicable_llm,
        tags=list(prompt.tags) if prompt.tags else [],
        snapshot_reason=reason,
    ).save()


def compute_field_changes(newer, version):
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
