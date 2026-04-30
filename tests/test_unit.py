import pytest

from api.admin_routes import TEMPLATE_VAR_PATTERN, render_prompt_preview
from api.config import DEFAULT_AUTH_TOKEN_PLACEHOLDER, get_auth_token


class TestTemplateVarPattern:
    def test_matches_simple_variable(self):
        match = TEMPLATE_VAR_PATTERN.search('Hello {{name}}')
        assert match is not None
        assert match.group(1) == 'name'

    def test_matches_variable_with_spaces(self):
        match = TEMPLATE_VAR_PATTERN.search('Hello {{ name }}')
        assert match is not None
        assert match.group(1) == 'name'

    def test_matches_underscore_variable(self):
        match = TEMPLATE_VAR_PATTERN.search('{{ my_var }}')
        assert match is not None
        assert match.group(1) == 'my_var'

    def test_matches_alphanumeric_variable(self):
        match = TEMPLATE_VAR_PATTERN.search('{{ var123 }}')
        assert match is not None
        assert match.group(1) == 'var123'

    def test_no_match_on_dash_variable(self):
        match = TEMPLATE_VAR_PATTERN.search('{{ my-var }}')
        assert match is None

    def test_no_match_on_number_start(self):
        match = TEMPLATE_VAR_PATTERN.search('{{ 123abc }}')
        assert match is None

    def test_finds_all_variables(self):
        text = '{{role}} is {{ domain }} expert {{level_1}}'
        matches = TEMPLATE_VAR_PATTERN.findall(text)
        assert matches == ['role', 'domain', 'level_1']

    def test_no_match_on_triple_braces(self):
        text = '{{{name}}}'
        matches = TEMPLATE_VAR_PATTERN.findall(text)
        assert 'name' in matches


class TestRenderPromptPreview:
    def test_simple_replacement(self):
        result = render_prompt_preview('Hello {{name}}', {'name': 'World'})
        assert result == 'Hello World'

    def test_multiple_replacements(self):
        result = render_prompt_preview('{{greeting}} {{name}}', {'greeting': 'Hi', 'name': 'Alice'})
        assert result == 'Hi Alice'

    def test_missing_key_preserved(self):
        result = render_prompt_preview('Hello {{name}}', {'other': 'value'})
        assert result == 'Hello {{name}}'

    def test_dict_value_serialized_as_json(self):
        result = render_prompt_preview('{{config}}', {'config': {'key': 'val'}})
        assert result == '{"key": "val"}'

    def test_list_value_converted_to_string(self):
        result = render_prompt_preview('{{items}}', {'items': [1, 2, 3]})
        assert result == '[1, 2, 3]'

    def test_none_content_returns_empty(self):
        assert render_prompt_preview(None, {'name': 'test'}) == ''

    def test_non_dict_example_returns_content(self):
        assert render_prompt_preview('Hello', 'not a dict') == 'Hello'

    def test_non_string_content_returns_empty(self):
        assert render_prompt_preview(123, {}) == ''

    def test_numeric_value_converted(self):
        result = render_prompt_preview('{{count}}', {'count': 42})
        assert result == '42'

    def test_no_expression_execution(self):
        result = render_prompt_preview('{{7*7}}', {})
        assert result == '{{7*7}}'

    def test_variable_with_spaces(self):
        result = render_prompt_preview('{{ name }}', {'name': 'Bob'})
        assert result == 'Bob'


class TestGetAuthToken:
    def test_returns_valid_token(self, monkeypatch):
        monkeypatch.setenv('AUTH_TOKEN', 'my-valid-token')
        assert get_auth_token() == 'my-valid-token'

    def test_returns_none_for_empty(self, monkeypatch):
        monkeypatch.delenv('AUTH_TOKEN', raising=False)
        assert get_auth_token() is None

    def test_returns_none_for_placeholder(self, monkeypatch):
        monkeypatch.setenv('AUTH_TOKEN', DEFAULT_AUTH_TOKEN_PLACEHOLDER)
        assert get_auth_token() is None

    def test_strips_whitespace(self, monkeypatch):
        monkeypatch.setenv('AUTH_TOKEN', '  my-token  ')
        assert get_auth_token() == 'my-token'

    def test_returns_none_for_whitespace_only(self, monkeypatch):
        monkeypatch.setenv('AUTH_TOKEN', '   ')
        assert get_auth_token() is None
