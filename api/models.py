from datetime import datetime

from marshmallow_mongoengine import ModelSchema
from mongoengine import Document, StringField,  ListField, DateTimeField, DictField


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

    meta = {'collection': 'prompts'}


class PromptSchema(ModelSchema):
    class Meta:
        model = Prompt
        exclude = ['id']
